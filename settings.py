import os

DEBUG = True

token = os.environ.get('RUSMAFIA_TG_BOT_TOKEN', None)

google_maps_key = os.environ.get('GOOGLE_MAPS_KEY', None)

mongo_connection_string = os.environ.get('RUSMAFIA_MONGO_CONNECTION_STRING', None)

if (None in (token, google_maps_key, mongo_connection_string)):
    print("Environmental variables are not set up properly")
    exit()

base_url = "https://api.telegram.org/bot" + token + "/"

time_format = '%m/%d/%y at %I:%M%p'

google_share_link_format = "https://calendar.google.com/event?action=TEMPLATE&tmeid={0}&tmsrc=sdrusmafia%40gmail.com"