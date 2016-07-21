====================
Weight Watchers Sync
====================

I am in no way affiliated with Weight Watchers. I just wanted
my fitbit account to sync better with my weight watchers one.

This app can be used to sync your food journal with Fitbit.

This app depends on a few things:
    1. You have a paid weight watcher's etools account
    2. You have created a fitbit api application

The sync app expects 4 environment variables defined
    WW_FB_ID - Your fitbit app client id
    WW_FB_SECRET - Your fitbit app client secret
    WW_SYNC_DB - The path the the sqllite database.
    WW_SYNC_ENCRYPTION_KEY - Key to encrypt and decrypt ww passwords

The encryption of the ww password is mildly silly. Perhaps I should be encypting everything? Perhaps its not worth bothering. Just... think a bit deeper if you take this and use it for people. WW passwords and the key for an app that should only need to view/edit food logs in fitbit is pretty low risk. But... still... put some thought into this if you choose to use this or have other use it.

running add_user.py will walk you though and adding a user to the database

With those defined you can run sync. It will first scrape weight watchers to
grab all your food for the current day. Then all fitbit food logs for the current
date will be cleared and replaced with weight watcher food logs

Optionally you can provide a date in the following format
'%Y-%m-%d' (Example: 2016-03-5)

If you do that the script will work with the provided date
