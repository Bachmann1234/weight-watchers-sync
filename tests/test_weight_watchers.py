import datetime
import json

import vcr
from tests.conftest import CASSETTES_HOME, FIXTURES_HOME
from wwsync.weight_watchers import get_foods_for_day, get_nutrition, WW_FOOD, get_food_detail, WW_RECIPE, \
    get_nutrition_info_for_day


def test_get_food_for_week(session):
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'food_for_2016_02_12')):
        foods = get_foods_for_day(session, datetime.datetime(2016, 2, 12))
        assert len(foods) == 15
        # These are the keys I expect
        food = foods[0]
        assert all(x in food for x in ['_id', 'versionId', 'portionName', 'portionSize'])


def test_get_calories_ww_defined_food(session):
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'egg_log.yaml')):
        # This object is actually quite more complicated. But I don't care
        food_log = {
            '_id': '561dcbbae33175473413d475',
            'versionId': '563c6669305d6e1834ab9485',
            'portionName': 'large',
            'sourceType': WW_FOOD,
            'portionSize': 2
        }
        assert get_nutrition(get_food_detail(session, food_log), food_log) == {
            'alcohol': 0.0,
            'calories': 144.0,
            'carbs': 0.72,
            'cholesterol': 0.0,
            'fat': 9.5,
            'fiber': 0.0,
            'protein': 12.56,
            'saturatedFat': 3.12,
            'sodium': 142.0,
            'sugar': 0.36,
            'sugarAlcohol': 0.0,
            'transFat': 0.0
        }


def test_get_calories_ww_recipe(session):
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'squash_recipe.yaml')):
        # This object is actually quite more complicated. But I don't care
        food_log = {
            '_id': '5673fac8e5ff06633497a53e',
            'versionId': '56754d41d147db5e34f33bfe',
            'portionName': 'large',
            'sourceType': WW_RECIPE,
            'portionSize': 1
        }
        assert get_nutrition(get_food_detail(session, food_log), food_log) == {
             'alcohol': 0.0,
             'calories': 137.40625,
             'carbs': 26.919925,
             'cholesterol': 0.0,
             'fat': 3.4685624999999995,
             'fiber': 4.625666666666667,
             'protein': 3.5154791666666663,
             'saturatedFat': 0.892375,
             'sodium': 217.77625,
             'sugar': 5.016041666666666,
             'sugarAlcohol': 0.0,
             'transFat': 0.0
        }


def test_day_in_life(username, password):
    with open("{}/{}".format(FIXTURES_HOME, 'food_for_day.json')) as infile:
        expected = json.loads(infile.read())
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'day_in_life.yaml')):
        result = get_nutrition_info_for_day(username, password, datetime.datetime(2016, 2, 21))
    assert expected == result
