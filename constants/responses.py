import random

def get_random_level():
    return random.randint(1, 23)

MESSAGE_RESPONSE = "Unfortunately, just like my owner, I'd prefer not to talk to certain people. Please use commands instead! :)"

WELCOME_MESSAGE = '''
Welcome to the mafia, {0} 😎

Here is a brief description of what I do:
I notify all our members about upcoming events to make sure \
that the mafia grows steadily.

- What do I do next?

You can check out ongoing /events, but otherwise - nothing really!
Just pay attention to notifications from me in order to stay connected.

We hope to to see you on our next event where we can 🤙👌✊🤫

Thank you for joining the Russian Mafia!

Contribute on <a href="https://github.com/dkubatko/Russian-Mafia-Telegram-bot">@github/dkubatko</a>

Note: If you see your name as "None", make sure you set up a username in Telegram and run /start again.

P.S.: I <i>do</i> have secrets. 🤐
'''

NOT_REGISTERED = "I don't think you've joined the mafia yet... Try /start"
PERMISSION_ERROR = f"This command can only be used by lvl 100 boss. Stay away lvl {get_random_level()} crook!"

IS_ADMIN = "Of course you are admin, my don!"
NOT_ADMIN = "You are not admin"

EVENT = '''
<b>Event:</b> {0}
<b>When:</b> {1}
<b>Where:</b> {2}
<b>What:</b> {3}
<b>Google Calendar:</b> <a href='{4}'>link</a>
<b>Organizer:</b> @{5}
'''

COMMAND_CANCELED = "Okay, rolling back..."

# New user joined

NEW_USER_JOINED = "@{0} has just joined the mafia! 🥳"

# Event builder questions

CREATE_EVENT_ERROR = "Something went wrong with the state of building the event."
CREATE_EVENT_NAME = "What would be the name of the new event?"
CREATE_EVENT_TIME = "Perfect! What time do you plan to meet for your event?\nUse the following format: 12/31/19 at 8:00pm"
CREATE_EVENT_TIME_FORMAT_FAIL = "Couldn't process that.\nOnce again, enter the time of your event as the following: 12/31/19 at 8:00pm"
CREATE_EVENT_LOCATION = "Got that. Where will the event happen?"
CREATE_EVENT_DESCRIPTION = "Good choice. Any other details you would want to share?"
CREATE_EVENT_DONE = "And... Done! Here's your event:"
CREATE_EVENT_CONFIRM = "Looks good?"
CREATE_EVENT_COMPLETE = "You have successfully created a new event! Check it out with /events"

# Event responses

NO_ONGOING_EVENTS = "No events are currently planned. I will make sure to notify you as soon as one gets created!"
CURRENT_EVENTS = "Here are the ongoing events:"

EVENT_GOING = "You and {0} others are going to event {1}!"
EVENT_NOT_GOING = "{0} others will miss you on the event {1} :("

EVENT_NOTIFICATION_SUCCESS = "Notified everyone about event {0}!"

EVENT_DISABLE_SUCCESS = "You have disabled event {0}"
EVENT_ENABLE_SUCCESS = "You have enabled event {0}!"

# Location
LOCATION_NOT_AVAILABLE = "Location is not available for event {0}"
LOCATION_REQUIRED = "Your location is required for event {0}.\nUse /location to grant access"
NO_LOCATION_RECORD = "I don't have access to your location. Use /location to grant access and receive directions to the event location."
LOCATION_REQUEST = "Would you mind sharing your location?"
LOCATION_RECEIVED = "Location captured. Thank you!"
LOCATION_FOR_EVENT = "This is the location for event {0}:"


# Attendees string builder

EVENT_ATTENDEE_LIST = "Here are {0} attendees for event {1}:\n"
EVENT_NO_ATTENDEES = "There are no attendees for event {0}"
EVENT_ATTENDEE = "@{0}\n"
EVENT_ATTENDEE_NO_USERNAME = "No display name, id: {0}\n"


# Notifications
EVENT_NOTIFICATION = "@{0} notified everyone about the following event:"

# Test blocked
TEST_BLOCKED = "This is just a test to see if you have blocked me. Please disregard this message.\nThere is no other way to test it and my owner is extremely stressed 😭"

# Secret mafia
SECRET_MAFIA_INVITATION = "You have been honored to receive an invitation to the Secret Russian Mafia (SRM). Would you accept your invitation?"
SM_INVITATION_ARGS = "Not enough arguments for /sm_invite [id]"
SM_INVITATION_USER_NOT_FOUND = "User with id {0} not found"
SM_INVITATION_ALREADY_MEMBER = "This user is already a member of the SRM!"
SM_INVITATION_EXPIRED = "You took too long to accept the invitation.\nApologize to the don and you might get another chance☝"
SM_INVITATION_SENT = "{0}(@{1}) has been notified with an invitation to the SRM!"
SM_INVITATION_ACCEPTED = '''
<i>Well, well don {0}.</i>

We welcome you in the secret society of outstanding individuals.

You might have been chosen due to your unique <b>skills</b>, extreme <b>intelligence</b>, enchanting <b>beauty</b>...

Or, most likely, just because you are friends with one of the well-known members.😅

Nonetheless, you have an opportunity to choose a secret nickname for youself. Just send it to me!
'''

SM_SECRET_NAME_RESPONSE = '''
HAHAHAHAHAHA

Wait, do you really think that {0} is a good nickname?!😬

What did they think when they invited you to join SRM?..🤥

Ahh, whatever. I'll just call you "Don {1}".

Welcome, anyway 🤗
'''

SM_INVITATION_DECLINED = "Pozor. You are still a member of the mafia, I guess...😒"

SM_NEW_MEMBER_NOTIFICATION = "Greet our new SRM member: {0}!"

SM_MESSAGE_ARGS = "Not enough arguments for /chat [message]"

SM_CHAT_MESSAGE = '''<b>S</b><b>R</b><b>M</b> [{0}]: 
<pre>{1}</pre>'''

SM_MESSAGE_SENT = "SRM message sent!"