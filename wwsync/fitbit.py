import webbrowser
from datetime import datetime

import sys

import base64
import requests

FITBIT_AUTH_URL = 'https://api.fitbit.com/oauth2/token?code={code}&client_id={client_id}&grant_type=authorization_code'
FITBIT_PERMISSION_SCREEN = 'https://fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&scope={scope}'
FITBIT_EDIT_FOOD_LOG_URL = 'https://api.fitbit.com/1/user/-/foods/log.json'
FITBIT_FOOD_UNIT_URL = 'https://api.fitbit.com/1/foods/units.json'
FITBIT_GET_FOOD_URL = 'https://api.fitbit.com/1/user/-/foods/log/date/{:%Y-%m-%d}.json'
FITBIT_DELETE_FOOD_URL = 'https://api.fitbit.com/1/user/-/foods/log/{log_id}.json'

DEFAULT_UNIT = 'unit'


def auth(code, client_id, secret):
    token = base64.b64encode("{}:{}".format(client_id, secret).encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic {}'.format(token),
    }
    auth_url = FITBIT_AUTH_URL.format(
        code=code,
        client_id=client_id
    )
    r = requests.post(auth_url, headers=headers)
    if r.status_code != 200:
        print("Auth Failed: {}".format(r.text))
        sys.exit(1)
    return r.json()


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
    response = requests.post(
        FITBIT_EDIT_FOOD_LOG_URL,
        data={
            'foodName': food_log['name'],
            'mealTypeId': ww_to_fitbit_meal[food_log['timeOfDay']],
            'unitId': unit_dict.get(ww_unit, unit_dict[DEFAULT_UNIT]),
            'amount': food_log['portionSize'],
            'date': "{:%Y-%m-%d}".format(date),
            'calories': int(nutrition_info['calories']),
            'sugars': nutrition_info['sugar'],
            'sodium': nutrition_info['sodium'],
            'protein': nutrition_info['protein'],
            'saturatedFat': nutrition_info['saturatedFat'],
            'totalFat': nutrition_info['fat'],
            'dietaryFiber': nutrition_info['fiber'],
            'totalCarbohydrate': nutrition_info['carbs']
        },
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
    response = requests.get(FITBIT_FOOD_UNIT_URL, headers=auth_header)
    response.raise_for_status()
    units = {}
    for unit in response.json():
        units[unit['name']] = unit['id']
    return units


def clear_food_logs(auth_header, date=datetime.now()):
    response = requests.get(FITBIT_GET_FOOD_URL.format(date), headers=auth_header)
    response.raise_for_status()
    food_logs = response.json()
    for log in food_logs['foods']:
        delete_response = requests.delete(
            FITBIT_DELETE_FOOD_URL.format(log_id=log['logId']),
            headers=auth_header
        )
        delete_response.raise_for_status()
