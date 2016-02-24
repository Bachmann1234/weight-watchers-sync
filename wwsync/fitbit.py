import webbrowser

import os
import sys

import base64
import requests

FITBIT_AUTH_URL = 'https://api.fitbit.com/oauth2/token?code={code}&client_id={client_id}&grant_type=authorization_code'
FITBIT_PERMISSION_SCREEN = 'https://fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&scope={scope}'


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


def main():
    client_id = os.environ['WW_FB_ID']
    secret = os.environ['WW_FB_SECRET']
    code = get_code(client_id)
    auth_response = auth(code, client_id, secret)
    print(auth_response)
    # Test api (stub)
    print(
        requests.get(
            'https://api.fitbit.com/1/user/{}/foods/log/goal.json'.format('27PLNC'),
            headers={'Authorization': 'Bearer {}'.format(auth_response['access_token'])}
        ).json()
    )


if __name__ == '__main__':
    main()
