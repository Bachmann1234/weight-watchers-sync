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
        food_log = {'portionId': '563c6669305d6e1834ab948d', 'sourceId': 58783, '_displayName': 'Egg(s)',
         'sourcePortionName': 'serving(s)', 'points': 4, 'isCore': True, 'name': 'Egg(s)',
         'entryId': 'ee1e26a0-4e37-11e6-8aa7-21442c64eff3', 'smartPointsPrecise': 2.0201, 'timeOfDay': 'morning',
         'sourcePortionId': 9, 'versionId': '563c6669305d6e1834ab9485', 'smartPoints': 4, 'portionTypeId': 800,
         'isActive': True, 'portionName': 'item(s)', 'portionSize': 2, 'isPowerFood': True, 'trackedDate': '2016-07-20',
         'sourceType': WW_FOOD, '_servingDesc': '2 item(s)', '_id': '561dcbbae33175473413d475',
         'pointsPrecise': 1.8347}
        food_detail = get_food_detail(session, food_log)
        result = get_nutrition(food_detail, food_log)
        assert result == {
            'calories': 144.0,
            'sodium': 142.0,
            'saturatedFat': 3.12,
            'carbs': 0.72,
            'sugar': 0.36,
            'fat': 9.5,
            'protein': 12.56
        }


def test_get_calories_ww_recipe(session):
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'steak_recipe.yaml')):
        # This object is actually quite more complicated. But I don't care
        food_log = {'smartPoints': 4, '_servingDesc': '1 serving(s)',
         '_displayName': 'Coffee-Chili Rubbed Flank Steak with Peppers and Onions', 'trackedDate': '2016-07-20',
         'pointsPrecise': 4.8926, 'portionSize': 1, 'isActive': True, 'entryId': '6fc42740-4e38-11e6-8237-3d072975d999',
         'points': 5, 'sourceId': 523991, 'smartPointsPrecise': 4, 'portionName': 'serving(s)',
         'name': 'Coffee-Chili Rubbed Flank Steak with Peppers and Onions', 'portionTypeId': None,
         'versionId': '57516df7f9984a6a3682ac0d', '_id': '57516df7f9984a6a3682ac0c', 'timeOfDay': 'morning',
         'sourcePortionName': 'serving(s)', 'sourcePortionId': None, 'sourceType': WW_RECIPE, 'portionId': None}
        result = get_nutrition(get_food_detail(session, food_log), food_log)
        assert result == {
            'sodium': 1089.58948,
            'protein': 26.27602775,
            'fiber': 2.48177325,
            'fat': 7.102034249999999,
            'sugar': 3.51908025,
            'saturatedFat': 2.4551232499999998,
            'carbs': 7.944517,
            'calories': 201.15632675
        }


def test_day_in_life(username, password):
    with open("{}/{}".format(FIXTURES_HOME, 'food_for_day.json')) as infile:
        expected = json.loads(infile.read())
    with vcr.use_cassette("{}/{}.yaml".format(CASSETTES_HOME, 'day_in_life.yaml')):
        result = get_nutrition_info_for_day(username, password, datetime.datetime(2016, 2, 21))
    assert expected == result
