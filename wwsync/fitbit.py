import json
import logging
import pprint

import os
import webbrowser
from datetime import datetime

import sys

import base64
import requests

FITBIT_AUTH_URL = 'https://api.fitbit.com/oauth2/token?code={code}&client_id={client_id}&grant_type=authorization_code'
FITBIT_AUTH_REFRESH_URL = ('https://api.fitbit.com/oauth2/token?'
                           'refresh_token={refresh_token}&grant_type=refresh_token')
FITBIT_PERMISSION_SCREEN = 'https://fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&scope={scope}'
FITBIT_EDIT_FOOD_LOG_URL = 'https://api.fitbit.com/1/user/-/foods/log.json'
FITBIT_FOOD_UNIT_URL = 'https://api.fitbit.com/1/foods/units.json'
FITBIT_GET_FOOD_URL = 'https://api.fitbit.com/1/user/-/foods/log/date/{:%Y-%m-%d}.json'
FITBIT_DELETE_FOOD_URL = 'https://api.fitbit.com/1/user/-/foods/log/{log_id}.json'

DEFAULT_UNIT = 'unit'


def _load_saved_auth(auth_file_path):
    try:
        with open(auth_file_path) as auth_file:
            auth_response = json.loads(auth_file.read())
    except (FileNotFoundError, TypeError, ValueError):
        auth_response = None
    return auth_response


def _do_auth(url, headers, auth_file_path):
    r = requests.post(url, headers=headers)
    if r.status_code != 200:
        print("Auth Failed: {}".format(r.text))
        sys.exit(1)
    with open(auth_file_path, 'w') as outfile:
        outfile.write(r.text)
    return r.json()


def refresh(auth_response, headers, auth_file_path):
    auth_url = FITBIT_AUTH_REFRESH_URL.format(
        refresh_token=auth_response['refresh_token']
    )
    logging.info("Refreshing auth token")
    return _do_auth(auth_url, headers, auth_file_path)


def auth(client_id, secret):
    auth_file_path = "{}/auth.json".format(os.path.dirname(os.path.abspath(__file__)))
    token = base64.b64encode("{}:{}".format(client_id, secret).encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic {}'.format(token),
    }
    saved_auth = _load_saved_auth(auth_file_path)
    if saved_auth:
        return refresh(saved_auth, headers, auth_file_path)
    else:
        code = get_code(client_id)
        auth_url = FITBIT_AUTH_URL.format(
            code=code,
            client_id=client_id
        )
        logging.info("logging into fitbit")
        return _do_auth(auth_url, headers, auth_file_path)


def get_code(client_id):
    """
    Opens a browser so the user can give us the auth code
    Args:
        client_id (str): client id for the app we want to use
    Returns:
        str: auth code user provided
    """
    url = FITBIT_PERMISSION_SCREEN.format(
        client_id=client_id,
        scope='nutrition'
    )
    webbrowser.open_new(url)
    print(
        "I am attempting to get permission to run. "
        "A browser should have just opened. If it has not please go to {}".format(
            url
        )
    )
    return input(
        "A browser should have just opened: please provide the the text after 'code=' so I can continue: "
    )


def make_food_log(
        auth_header,
        ww_food_entry,
        unit_dict,
        date=datetime.now()
):
    """
    Converts a ww food entry and saves it to fitbit
    Args:
        auth_header:
            Authorization header for fitbit
        ww_food_entry:
            A dict with nutrition_info and food_log that will be used to record
        unit_dict:
            Result of a previous call to get_units, dict
        date:
            Date of the food log
    """
    # 2 is morning snack and 4 is afternoon snack but I
    # don't have ww equivalents for that
    ww_to_fitbit_meal = {
        'morning': 1,
        'midday': 3,
        'evening': 5,
        'anytime': 7,
    }
    food_log = ww_food_entry['food_log']
    nutrition_info = ww_food_entry['nutrition_info']
    ww_unit = food_log['portionName'].replace('(s)', '')
    data = {
        'foodName': food_log['name'],
        'mealTypeId': ww_to_fitbit_meal[food_log['timeOfDay']],
        'unitId': unit_dict.get(ww_unit, unit_dict[DEFAULT_UNIT]),
        'amount': food_log['portionSize'],
        'date': "{:%Y-%m-%d}".format(date),
        'calories': int(nutrition_info['calories']),
        'sugars': nutrition_info.get('sugar', -1),
        'sodium': nutrition_info.get('sodium', -1),
        'protein': nutrition_info.get('protein', -1),
        'saturatedFat': nutrition_info.get('saturatedFat', -1),
        'totalFat': nutrition_info.get('fat', -1),
        'dietaryFiber': nutrition_info.get('fiber', -1),
        'totalCarbohydrate': nutrition_info.get('carbs', -1)
    }
    for key in data.copy().keys():
        if data[key] == -1:
            del(data[key])

    logging.info("Logging food: {}".format(food_log['name']))

    response = requests.post(
        FITBIT_EDIT_FOOD_LOG_URL,
        data=data,
        headers=auth_header
    )
    response.raise_for_status()


def get_units(auth_header):
    """
    Calls out to fitbit to get the most up to date units
    Args:
        auth_header:
            Authorization info for fitbit
    returns:
        dict from unit name to unit id
    """
    logging.info("Grabbing Units")
    response = requests.get(FITBIT_FOOD_UNIT_URL, headers=auth_header)
    response.raise_for_status()
    units = {}
    for unit in response.json():
        units[unit['name']] = unit['id']
    return units


def get_food_logs(auth_header, date=datetime.now()):
    logging.info("Requesting current fitbit food logs")
    response = requests.get(FITBIT_GET_FOOD_URL.format(date), headers=auth_header)
    response.raise_for_status()
    return response.json()


def clear_food_logs(auth_header, food_logs):
    for log in food_logs['foods']:
        logging.info("Deleting {}".format(log['loggedFood']['name']))
        delete_response = requests.delete(
            FITBIT_DELETE_FOOD_URL.format(log_id=log['logId']),
            headers=auth_header
        )
        delete_response.raise_for_status()
    logging.info("Done deleting logs")


def main():
    logging.basicConfig(level='INFO')
    client_id = os.environ['WW_FB_ID']
    secret = os.environ['WW_FB_SECRET']
    auth_response = auth(client_id, secret)
    auth_header = {'Authorization': 'Bearer {}'.format(auth_response['access_token'])}
    pprint.pprint(get_food_logs(auth_header))

if __name__ == '__main__':
    main()
