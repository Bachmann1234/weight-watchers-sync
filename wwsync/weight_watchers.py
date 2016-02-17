import datetime
import getpass

import requests
import sys

from bs4 import BeautifulSoup

WW_HOME_PAGE = "https://cmx.weightwatchers.com"
WW_LOGIN_URL = 'https://login.weightwatchers.com/classic/UI/Login'
WW_JOURNAL_URL = '{host}/api/v2/cmx/members/~/trackedFoods/{date}'
FOOD_URL = '{host}/api/v2/public/foods/{food_id}/{version_id}'


def get_nutrition_information(session, food_log):
    """
    Args:
        session (requests.Session) : An authenticated ww session
        food_log (dict) : A food entry
    Returns:
         (dict) ww food objects
    """
    # I predict this will change as I deal with different kinds of foods
    food_info = session.get(
        FOOD_URL.format(
            host=WW_HOME_PAGE,
            food_id=food_log['_id'],
            version_id=food_log['versionId']
        )
    )
    return food_info.json()


def get_foods_for_day(session, date):
    """Gets the ww foods logged at the provided date
    Args:
        session (requests.Session) : An authenticated ww session
        date (datetime.datetime): Date to retrieve
    Returns:
         (dict) ww food objects
    """
    response = session.get(
        WW_JOURNAL_URL.format(
            host=WW_HOME_PAGE,
            date=date.strftime('%Y-%m-%d')
        )
    )
    response.raise_for_status()
    return response.json()


def login(username, password, session):
    """
    Authenticates the provided session
    Args:
        username (str): Username String
        password (str): Password String
        session (requests.Session): an unauthenticated session
    Returns:
        The session passed in except now its authenticated
    """
    initial_url = '{}{}'.format(WW_LOGIN_URL, '?realm=US&service=ldapService&goto=http%3a%2f%2fcmx.weightwatchers.com')
    session.headers.setdefault('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) '
                                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                                             'Chrome/48.0.2564.109 Safari/537.36')
    response = session.get(initial_url)  # set headers cookies etc
    soup = BeautifulSoup(response.text, 'html.parser')
    login_parameters = {
        x.get('name'): x.get('value')
        for x in soup.find_all('input')
        if x.get('name') != 'Login.Submit'
    }
    login_parameters['IDToken1'] = username
    login_parameters['IDToken2'] = password
    login_parameters['pcookie'] = 'on'
    response = session.post(
        WW_LOGIN_URL,
        data=login_parameters,
        headers=dict(referer=initial_url)
    )
    response.raise_for_status()
    return session


def get_calories(nutritional_info, food_log):
    """
    Pulls the correct information out of the nutritional info based
    on the provided food_log
    Args:
        nutritional_info (dict): WW food info of the food the food log is tracking
        food_log (dict): food entry logging the food nutritional info was passed in
    """
    log_portion = food_log['portionName']
    portions_ate = food_log['portionSize']
    portions = nutritional_info['portions']
    for portion in portions:
        if portion['name'] == log_portion:
            return portion['nutrition']['calories'] * portions_ate
    raise ValueError("Failed to find portion {}".format(log_portion))


def main(username, password):
    session = login(username, password, requests.Session())
    return sum(get_calories(get_nutrition_information(session, food_log), food_log)
               for food_log in get_foods_for_day(session, datetime.datetime.now()))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        main(input("Username: "), getpass.getpass())
    else:
        main(sys.argv[1], sys.argv[2])
