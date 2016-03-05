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
    WW_USER - Your Weight Watchers Username
    WW_PASSWD - Your Weight Watchers Password

With those defined you can run sync. It will first scrape weight watchers to
grab all your food for the current day. Then all fitbit food logs for the current
date will be cleared and replaced with weight watcher food logs

Optionally you can provide a date in the following format
'%Y-%m-%d' (Example: 2016-03-5)

If you do that the script will work with the provided date