import datetime
import logging
import pprint

import sys

import os
from wwsync.fitbit import auth, get_units, clear_food_logs, make_food_log, get_food_logs
from wwsync.weight_watchers import get_nutrition_info_for_day


def main():
    if len(sys.argv) > 1:
        date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
    else:
        date = datetime.datetime.now()
    logging.basicConfig(level='INFO')
    client_id = os.environ['WW_FB_ID']
    secret = os.environ['WW_FB_SECRET']
    nutritional_info_for_day = get_nutrition_info_for_day(
        os.environ['WW_USER'],
        os.environ['WW_PASSWD'],
        date=date
    )
    auth_response = auth(client_id, secret)
    auth_header = {'Authorization': 'Bearer {}'.format(auth_response['access_token'])}
    units = get_units(auth_header)
    clear_food_logs(auth_header, get_food_logs(auth_header, date=date))

    for log in nutritional_info_for_day:
        make_food_log(
            auth_header,
            log,
            units,
            date=date
        )
    # print final result
    pprint.pprint(get_food_logs(auth_header))


if __name__ == '__main__':
    main()
