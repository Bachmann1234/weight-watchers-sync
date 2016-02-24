import datetime
import getpass
import os

from collections import defaultdict
from pprint import pprint

import requests
import sys

from bs4 import BeautifulSoup

WW_HOME_PAGE = "https://cmx.weightwatchers.com"
WW_LOGIN_URL = 'https://login.weightwatchers.com/classic/UI/Login'
WW_JOURNAL_URL = '{host}/api/v2/cmx/members/~/trackedFoods/{date}'
FOOD_URL = '{host}/api/v2/public/foods/{food_id}/{version_id}'
RECIPE_URL = '{host}/api/v2/public/recipes/{food_id}/{version_id}?fullDetails=true'
MEMBER_FOOD_URL = '{host}/api/v2/cmx/members/~/custom-foods/foods/{food_id}/{version_id}?fullDetails=true'
MEMBER_RECIPE_URL = '{host}/api/v2/cmx/members/~/custom-foods/recipes/{food_id}/{version_id}?fullDetails=true'

WW_FOOD = 'WWFOOD'
MEMBER_FOOD = 'MEMBERFOOD'
WW_RECIPE = 'WWRECIPE'
WW_VENDOR_FOOD = 'WWVENDORFOOD'
MEMBER_RECIPE = 'MEMBERRECIPE'


def get_food_detail(session, food_log):
    """
    Args:
        session (requests.Session) : An authenticated ww session
        food_log (dict) : A food entry
    Returns:
         (dict) ww food objects
    """
    nutritional_urls = {
        WW_FOOD: FOOD_URL,
        WW_VENDOR_FOOD: FOOD_URL,
        WW_RECIPE: RECIPE_URL,
        MEMBER_FOOD: MEMBER_FOOD_URL,
        MEMBER_RECIPE: MEMBER_RECIPE_URL,
    }
    source = food_log['sourceType']
    food_info = session.get(
        nutritional_urls[source].format(
            host=WW_HOME_PAGE,
            food_id=food_log['_id'],
            version_id=food_log['versionId']
        )
    )
    food_info.raise_for_status()
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


def get_nutrition(nutritional_info, food_log):
    """
    Pulls the correct information out of the nutritional info based
    on the provided food_log
    Args:
        nutritional_info (dict): WW food info of the food the food log is tracking
        food_log (dict): food entry logging the food nutritional info was passed in
    """
    nutrition_extractors = {
        WW_RECIPE: get_nutrition_for_recipe,
        WW_FOOD: get_nutrition_for_food,
        WW_VENDOR_FOOD: get_nutrition_for_food,
        MEMBER_FOOD: get_nutrition_for_food,
        MEMBER_RECIPE: get_nutrition_for_recipe,
    }
    source = food_log['sourceType']
    return nutrition_extractors[source](nutritional_info, food_log)


def get_nutrition_for_recipe(nutritional_info, food_log):
    ingredient_nutritional_infos = [
        _get_nutrition_for_food(
            ingredient['itemDetail'],
            ingredient['portionName'],
            ingredient['quantity']
        ) for ingredient in nutritional_info['ingredients']
    ]
    sum_of_ingredients = sum_nutrition_info(ingredient_nutritional_infos)

    return nutrition_times_portion(sum_of_ingredients, food_log['portionSize']/nutritional_info['servingSize'])


def sum_nutrition_info(nutritional_infos):
    """
    Combine the nutritional infos provided
    Args:
        nutritional_infos list[dict]: nutritional infos to be combined
    Returns:
        The sum of the dicts. If a key is missing in one of the dicts we assume
        a value of zero for that key
    """
    result = defaultdict(float)
    for key in nutritional_infos[0].keys():
        for ingredient_nutritional_info in nutritional_infos:
            result[key] += float(ingredient_nutritional_info.get(key, 0))
    return result


def get_nutrition_for_food(nutritional_info, food_log):
    """
    Pulls the correct information out of the nutritional info based
    on the provided food_log
    Args:
        nutritional_info (dict): WW food info of the food the food log is tracking
        food_log (dict): food entry logging the food nutritional info was passed in
    """
    return _get_nutrition_for_food(nutritional_info, food_log['portionName'], food_log['portionSize'])


def _get_nutrition_for_food(nutritional_info, portion_name, amount_consumed):
    portions = nutritional_info['portions']
    for portion in portions:
        if portion['name'] == portion_name:
            return nutrition_times_portion(portion['nutrition'], amount_consumed/portion['size'])
    raise ValueError("Failed to find portion {}".format(portion_name))


def nutrition_times_portion(nutritional_info, portions):
    """
    Simply multiplication
    Args:
        nutritional_info (dict): Nutritional info for 1 portion
        portions (int): portions to multiply by
    returns:
        dict with values multiplied by portions
    """
    return {key: (float(value) * float(portions)) for key, value in nutritional_info.items()}


def get_nutrition_info_for_day(username, password, date=None):
    if date is None:
        date = datetime.datetime.now()
    session = login(username, password, requests.Session())
    result = []
    food_logs = get_foods_for_day(session, date)
    for food_log in food_logs:
        result.append({
            "food_log": food_log,
            "nutrition_info": get_nutrition(get_food_detail(session, food_log), food_log)
        })
    return result

if __name__ == '__main__':
    nutritional_info_for_day = get_nutrition_info_for_day(os.environ['WW_USER'], os.environ['WW_PASSWD'])
    pprint(nutritional_info_for_day)
    pprint(dict(sum_nutrition_info(list(n["nutrition_info"] for n in nutritional_info_for_day))))
