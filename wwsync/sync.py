import logging

import os
from wwsync.fitbit import get_code, auth, get_units, clear_food_logs, make_food_log
from wwsync.weight_watchers import get_nutrition_info_for_day


def main():
    logging.basicConfig(level='INFO')
    client_id = os.environ['WW_FB_ID']
    secret = os.environ['WW_FB_SECRET']
    nutritional_info_for_day = get_nutrition_info_for_day(
        os.environ['WW_USER'],
        os.environ['WW_PASSWD']
    )
    code = get_code(client_id)
    auth_response = auth(code, client_id, secret)
    auth_header = {'Authorization': 'Bearer {}'.format(auth_response['access_token'])}
    units = get_units(auth_header)
    clear_food_logs(auth_header)

    for log in nutritional_info_for_day:
        make_food_log(
            auth_header,
            log,
            units
        )


if __name__ == '__main__':
    main()
