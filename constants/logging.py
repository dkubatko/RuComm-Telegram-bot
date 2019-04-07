LOG_FORMATTER = '%(asctime)s / %(name)s / %(levelname)s\n'\
        '| FILE: %(filename)s FUNCTION: %(funcName)s LINE: %(lineno)d |\nMESSAGE: %(message)s'

BOT_LOG_FILE = "logs/bot.log"

DB_CONNECTED = "Connected to DB"

BOT_START = "Starting bot"

GOOGLE_CALENDAR_CONNECTED = "Connected to Google Calendar"

GOOGLE_CALENDAR_EVENT_CREATED = "Event {0} added to the calendar"

INVALID_USER_STATE = "Invalid user state: {0}"

CALLBACK_QUERY_ERROR = "Callback query error"

COMMAND_START = "User: <{0}> fired start command"

DB_USER_ADDED = "User <{0}> with id <{1}> added to the database"

DB_USER_UPDATED = "User <{0}> with id <{1}> updated in the database"

DB_USER_NOT_FOUND = "User with id <{0}> not found"

DB_EVENT_ADDED = "Event <{0}> with id <{1}> added to the database"

DB_EVENT_UPDATED = "Event <{0}> with id <{1}> updated in the database"

DB_EVENT_NOT_FOUND = "Event with id <{0}> not found"

EVENT_NO_ONGOING = "User <{0}> with id <{1}> event list: no ongoing events returned from DB"

EVENT_ONGOING = "User <{0}> with id <{1}> event list: return {2} events"

EVENT_NOTIFY = "User <{0}> with id <{1}> notified about event <{2}>"

EVENT_GOING = "User <{0}> with id <{1}> is going to event <{2}>"

EVENT_NOT_GOING = "User <{0}> with id <{1}> is not going to event <{2}>"

EVENT_DISABLED = "User <{0}> with id <{1}> disabled event <{2}>"

EVENT_ENABLED = "User <{0}> with id <{1}> enabled event <{2}>"

LOCATION_RECEIVED = "User <{0}> with id <{1}> has shared their location"

NEW_MEMBER_NOTIFIED = "Notified all users about new member <{0}> with id <{1}>"