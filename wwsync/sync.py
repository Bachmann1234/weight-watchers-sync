import datetime
import logging

import sys
import traceback

import os
from wwsync.fitbit import auth, get_units, clear_food_logs, make_food_log, get_food_logs
from wwsync.weight_watchers import get_nutrition_info_for_day


def setup_logging():
    logging.basicConfig(level='INFO', format='%(asctime)s %(message)s')

    def log_exceptions(exctype, value, tb):
        """
        Make sure any uncaught exceptions are logged
        """
        logging.error("Uncaught Exception: {} - {}\n{}".format(exctype.__name__, value, ''.join(traceback.format_tb(tb))))
        sys.__excepthook__(exctype, value, tb)
    sys.excepthook = log_exceptions


def main():
    if len(sys.argv) > 1:
        date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
    else:
        date = datetime.datetime.now()
    setup_logging()
    logging.info("Updating foods for {}".format("{:%Y-%m-%d}".format(date)))
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
    logging.info("Sync Complete")


if __name__ == '__main__':
    main()
