import datetime

import vcr
from tests.conftest import CASSETTES_HOME
from wwsync.weight_watchers import get_foods_for_day, get_nutrition_information, get_calories


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
            'portionSize': 2
        }
        assert get_calories(get_nutrition_information(session, food_log), food_log) == 144
