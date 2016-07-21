import json
import os
import sys
from getpass import getpass

from wwsync.encrypt import encrypt
from wwsync.fitbit import auth

from wwsync.models import User, get_db_session


def main():
    db_session = get_db_session()
    client_id = os.environ['WW_FB_ID']
    fb_secret = os.environ['WW_FB_SECRET']

    print("This will walk you though making a new user. First it will ask for permission to access fitbit")
    fitbit_info = auth(client_id, fb_secret)

    print("Now I need your weightwatcher username and password. "
          "this is because Weight Watchers does not provide an api with oauth")
    ww_username = input("Weight watchers username: ")

    # This is *probably* silly since my initial implementation will use a database file. So if you get the file
    # You will probably figure out how to find the key (hint, its an environment variable).
    # If this is productionalized further the database would need to be on a separate host and further thought
    # is required. But why not encrypt your password

    # However, I dont plan on hosting this for people I dont know since I am using undocumented ww apis
    # And if WW does make an api it will hopefully not have oauth
    ww_password = encrypt(getpass("Weight Watcher password: ").encode('utf-8'))

    user = User(fitbit_tokens=json.dumps(fitbit_info), ww_username=ww_username, ww_password=ww_password)
    db_session.add(user)
    db_session.commit()
    return 0

if __name__ == '__main__':
    sys.exit(main())
