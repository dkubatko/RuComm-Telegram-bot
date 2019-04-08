from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import settings
from datetime import datetime
import constants.logging as logging_settings
import constants.responses as responses
import logging
from mongo_driver import MongoDriver
from models.user import User
from models.event import Event
from telegram.error import TelegramError
from google_calendar import GoogleCalendarAPI
import traceback

class RusMafiaBot:
    def __init__(self, token):
        self.token = token
        self.setup_logging()

        self.db_driver = MongoDriver(settings.mongo_connection_string)
        self.logger.info(logging_settings.DB_CONNECTED)

        self.gcalendar = GoogleCalendarAPI()
        self.logger.info(logging_settings.GOOGLE_CALENDAR_CONNECTED)

        self.updater = Updater(token=token, use_context=True)
        dispatcher = self.updater.dispatcher

        # command handlers
        start_handler = CommandHandler('start', self.command_start)
        admin_handler = CommandHandler('admin', self.command_admin)
        cancel_handler = CommandHandler('cancel', self.command_cancel)
        create_event_handler = CommandHandler('create_event', self.command_create_event)
        list_events_handler = CommandHandler('events', self.command_list_events, pass_user_data=True)
        command_location_handler = CommandHandler('location', self.command_grant_location)
        # other handlers
        command_query_handler = CallbackQueryHandler(self.command_query_callback, pass_user_data=True)
        echo_handler = MessageHandler(Filters.text, self.message_default)
        location_handler = MessageHandler(Filters.location, self.handle_location)
        

        dispatcher.add_handler(echo_handler)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(admin_handler)
        dispatcher.add_handler(cancel_handler)
        dispatcher.add_handler(list_events_handler)
        dispatcher.add_handler(create_event_handler)
        dispatcher.add_handler(command_query_handler)
        dispatcher.add_handler(location_handler)
        dispatcher.add_handler(command_location_handler)
        
        dispatcher.add_error_handler(self.error_callback)

    def setup_logging(self):
        self.logger = logging.getLogger('bot')
        log_f = logging.FileHandler(logging_settings.BOT_LOG_FILE)
        log_s = logging.StreamHandler()

        if (settings.DEBUG):
            self.logger.setLevel(logging.DEBUG)
            log_f.setLevel(logging.DEBUG)
            log_s.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(logging_settings.LOG_FORMATTER)
        log_f.setFormatter(formatter)
        log_s.setFormatter(formatter)

        self.logger.addHandler(log_f)
        self.logger.addHandler(log_s)

    def start(self, clean=False):
        self.logger.info(logging_settings.BOT_START)
        self.updater.start_polling(clean=clean)

    # Command handlers
    
    def command_start(self, update, context):
        username = update.message.from_user.username
        self.logger.info(logging_settings.COMMAND_START.format(username))
        
        # create new user
        new_user = User(update.message.from_user.id, username, update.message.chat_id)

        is_new = self.db_driver.add_user(new_user)

        if (is_new and new_user.display_name):
            self.new_member_notify(context, new_user)
            self.logger.info(logging_settings.NEW_MEMBER_NOTIFIED.format(new_user.display_name, new_user.id))

        context.bot.send_message(chat_id=update.message.chat_id, 
                text = responses.WELCOME_MESSAGE.format(username), 
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)

    def command_admin(self, update, context):
        user_id = update.message.from_user.id
        user = self.db_driver.get_user(user_id)

        if not user:
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_REGISTERED)
            return
        
        if (user.admin):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.IS_ADMIN)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_ADMIN)
    
    def command_cancel(self, update, context):
        user_id = update.message.from_user.id
        user = self.db_driver.get_user(user_id)

        if not user:
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_REGISTERED)
            return
        
        # Clear the state
        user.fields['state'] = None
        self.db_driver.update_user(user)

        # Remove keyboard if there was one
        reply_markup = ReplyKeyboardRemove()
        context.bot.send_message(chat_id=update.message.chat_id, text = responses.COMMAND_CANCELED, reply_markup=reply_markup)

    def command_create_event(self, update, context):
        user_id = update.message.from_user.id
        user = self.db_driver.get_user(user_id)

        if not user:
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_REGISTERED)
            return

        if not (user.admin):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.PERMISSION_ERROR)
            return
        
        state = user.fields.get('state', None)
        
        if state is None:
            state = 'event_create_start'
            user.fields['state'] = state
            user.fields['new_event'] = Event().to_json()
            self.db_driver.update_user(user)
        
        self.handle_state(update, context, user)

    # Message handlers

    def message_default(self, update, context):
        user_id = update.message.from_user.id
        user = self.db_driver.get_user(user_id)

        if (user is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_REGISTERED)
            return
        
        if (user.fields.get('state', None) is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.MESSAGE_RESPONSE)
            return

        # handle state of the conversation
        self.handle_state(update, context, user)

    # Handle state of the bot-user conversation

    def handle_state(self, update, context, user):
        state = user.fields.get('state', None)

        if (state == 'event_create_start'):
            self.create_event_start(update, context, user)
        elif (state == 'event_create_name'):
            self.create_event_name(update, context, user)
        elif (state == 'event_create_time'):
            self.create_event_time(update, context, user)
        elif (state == 'event_create_location'):
            self.create_event_location(update, context, user)
        elif (state == 'event_create_description'):
            self.create_event_description(update, context, user)
        elif (state == 'event_create_save'):
            self.create_event_save(update, context, user)
        elif (state == 'event_create_cancel'):
            self.create_event_cancel(update, context, user)
        else:
            self.logger.error(logging_settings.INVALID_USER_STATE.format(state))

    def create_event_start(self, update, context, user):
        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_NAME)
        user.fields['state'] = 'event_create_name'
        self.db_driver.update_user(user)

    def create_event_name(self, update, context, user):
        name = update.message.text
        new_event = user.fields.get('new_event')

        # Handle event builder failure
        if (new_event is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_ERROR)
            user.fields['state'] = None
            self.db_driver.update_user(user)
            return
        
        new_event['name'] = name
        # Save event state
        user.fields['new_event'] = Event(**new_event).to_json()
        user.fields['state'] = 'event_create_time'
        self.db_driver.update_user(user)

        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_TIME)

    def check_time_format(self, s):
        try:
            datetime.strptime(s, settings.time_format)
            return True
        except ValueError: 
            return False

    def create_event_time(self, update, context, user):
        time = update.message.text

        # if can't proccess the time
        if (not self.check_time_format(time)):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_TIME_FORMAT_FAIL)
            return

        new_event = user.fields.get('new_event')

        # Handle event builder failure
        if (new_event is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_ERROR)
            user.fields['state'] = None
            self.db_driver.update_user(user)
            return
        
        new_event['time'] = time
        # Save event state
        user.fields['new_event'] = Event(**new_event).to_json()
        user.fields['state'] = 'event_create_location'
        self.db_driver.update_user(user)

        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_LOCATION)

    def create_event_location(self, update, context, user):
        location = update.message.text
        new_event = user.fields.get('new_event')

        # Handle event builder failure
        if (new_event is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_ERROR)
            user.fields['state'] = None
            self.db_driver.update_user(user)
            return
        
        new_event['location'] = location
        # Save event state
        user.fields['new_event'] = Event(**new_event).to_json()
        user.fields['state'] = 'event_create_description'
        self.db_driver.update_user(user)

        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_DESCRIPTION)
    
    def create_event_description(self, update, context, user):
        description = update.message.text
        new_event = user.fields.get('new_event')

        # Handle event builder failure
        if (new_event is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_ERROR)
            user.fields['state'] = None
            self.db_driver.update_user(user)
            return
        
        new_event['description'] = description
        # Save event state
        e = Event(**new_event)
        user.fields['new_event'] = e.to_json()
        user.fields['state'] = None
        self.db_driver.update_user(user)

        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_DONE)
        context.bot.send_message(chat_id=update.message.chat_id, text = e.format(), parse_mode=ParseMode.HTML)
        
        # Add answer options
        keyboard = [[InlineKeyboardButton("Yes!", callback_data='event_save'),
                InlineKeyboardButton("Nope...", callback_data='event_cancel')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_CONFIRM, 
                    reply_markup=reply_markup)

    def create_event_save(self, update, context, user):
        new_event = user.fields.get('new_event')
        
        if (new_event is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_ERROR)
            user.fields['state'] = None
            self.db_driver.update_user(user)
            return

        e = Event(**new_event)

        # create calendar event
        event_url = self.gcalendar.create_event(e)
        self.logger.info(logging_settings.GOOGLE_CALENDAR_EVENT_CREATED.format(e.name))
        e.fields['google_calendar_url'] = event_url
        self.db_driver.add_event(e)

        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CREATE_EVENT_COMPLETE)

        # Clear user's state and data
        user.fields['state'] = None
        user.fields['new_event'] = None
        
        # Add event to the creator user events
        user.events.append(e.id)

        self.db_driver.update_user(user)

    def create_event_cancel(self, update, context, user):
        user.fields['state'] = None
        self.db_driver.update_user(user)
        context.bot.send_message(chat_id=update.message.chat_id, text = responses.COMMAND_CANCELED)
        
    # Handles on-screen button presses
    def command_query_callback(self, update, context):
        query = update.callback_query

        if (query is None):
            self.logger.error(logging_settings.CALLBACK_QUERY_ERROR)
            return
        
        query.answer()
        
        user_id = query.from_user.id
        user = self.db_driver.get_user(user_id)

        if not user:
            context.bot.send_message(chat_id=query.message.chat_id, text = responses.NOT_REGISTERED)
            return

        action = query.data

        # Non-admin event callbacks

        message_id = query.message.message_id

        if ('event_going' in action):
            # get the event id
            event_id = action.split('_')[-1]
            self.event_going(context, user, self.db_driver.get_event(event_id), message_id)
            return
        elif ('event_not_going' in action):
            # get the event id
            event_id = action.split('_')[-1]
            self.event_not_going(context, user, self.db_driver.get_event(event_id), message_id)
            return
        elif ('event_location' in action):
            # get the event id
            event_id = action.split('_')[-1]
            self.show_event_location(context, user, self.db_driver.get_event(event_id))
            return

        # Admin event callbacks

        if not (user.admin):
            context.bot.send_message(chat_id=query.message.chat_id, text = responses.PERMISSION_ERROR)
            return
        
        if (action == 'event_save'):
            user.fields['state'] = 'event_create_save'

            # remove confirm message
            context.bot.delete_message(user.chat_id, message_id)

            self.handle_state(query, context, user)
            return
        elif (action == 'event_cancel'):
            user.fields['state'] = 'event_create_cancel'

            # remove confirm message
            context.bot.delete_message(user.chat_id, message_id)

            self.handle_state(query, context, user)
            return
        elif ('event_notify' in action):
            event_id = action.split('_')[-1]
            self.event_notify(context, user, self.db_driver.get_event(event_id))
            return
        elif ('event_disable' in action):
            event_id = action.split('_')[-1]
            self.event_disable(context, user, self.db_driver.get_event(event_id), message_id)
            return
        elif ('event_enable' in action):
            event_id = action.split('_')[-1]
            self.event_enable(context, user, self.db_driver.get_event(event_id), message_id)
            return
        elif ('event_attendees' in action):
            event_id = action.split('_')[-1]
            self.event_attendees(context, user, self.db_driver.get_event(event_id))
            return
        

        self.db_driver.update_user(user)

    def event_notify(self, context, init_user: User, event: Event):
        users = self.db_driver.get_all_users()

        for user in users:
            if (user.id == init_user.id):
                continue
                
            chat_id = user.chat_id
            self.show_event(context, event, user, chat_id)

            self.logger.info(logging_settings.EVENT_NOTIFY.format(user.display_name, user.id, event.name))
        
        context.bot.send_message(chat_id=init_user.chat_id, text = responses.EVENT_NOTIFICATION_SUCCESS.format(event.name))

    def event_disable(self, context, user: User, event: Event, message_id):
        # Set event as not ongoing
        event.ongoing = False
        self.db_driver.update_event(event)

        self.logger.info(logging_settings.EVENT_DISABLED.format(user.display_name, user.id, event.name))

        # Change reply markup to reflect the change
        location_button = InlineKeyboardButton("Location",
                callback_data="event_location_" + event.id)
        keyboard = [[InlineKeyboardButton("Notify!", 
                    callback_data='event_notify_' + event.id)],
                    [InlineKeyboardButton("Enable",
                    callback_data='event_enable_' + event.id)],
                    [location_button]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.edit_message_reply_markup(chat_id=user.chat_id, 
            message_id=message_id, reply_markup = reply_markup)

        context.bot.send_message(chat_id=user.chat_id, text = responses.EVENT_DISABLE_SUCCESS.format(event.name))

    def event_enable(self, context, user: User, event: Event, message_id):
        # Set event as not ongoing
        event.ongoing = True
        self.db_driver.update_event(event)

        self.logger.info(logging_settings.EVENT_ENABLED.format(user.display_name, user.id, event.name))

        # Change reply markup to reflect the change
        location_button = InlineKeyboardButton("Location",
                callback_data="event_location_" + event.id)
        keyboard = [[InlineKeyboardButton("Notify!", 
                    callback_data='event_notify_' + event.id)],
                    [InlineKeyboardButton("Disable",
                    callback_data='event_disable_' + event.id)],
                    [location_button]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.edit_message_reply_markup(chat_id=user.chat_id, 
            message_id=message_id, reply_markup = reply_markup)

        context.bot.send_message(chat_id=user.chat_id, text = responses.EVENT_ENABLE_SUCCESS.format(event.name))
    
    def event_attendees(self, context, user: User, event: Event):
        # Get attendee list
        attendees = self.get_event_attendees(event)
        
        response = responses.EVENT_ATTENDEE_LIST.format(len(attendees), event.name)

        for attendee in attendees:
            name = responses.EVENT_ATTENDEE.format(attendee.display_name)

            if attendee.display_name is None:
                name = responses.EVENT_ATTENDEE_NO_USERNAME.format(attendee.id)

            response += name
        
        if (len(attendees) == 0):
            response = responses.EVENT_NO_ATTENDEES.format(event.name)
        
        context.bot.send_message(chat_id=user.chat_id, text = response)
        
    
    def event_going(self, context, user: User, event: Event, message_id):
        # add to the list of going-to events if wasn't already
        if (event.id not in user.events):
            user.events.append(event.id)
        
        self.db_driver.update_user(user)

        self.logger.info(logging_settings.EVENT_GOING.format(user.display_name, user.id, event.id))

        # Change reply markup to reflect the change
        location_button = InlineKeyboardButton("Location",
                callback_data="event_location_" + event.id)
        keyboard = [[InlineKeyboardButton("I changed my mind", 
                    callback_data = 'event_not_going_' + event.id)],
                    [location_button]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.edit_message_reply_markup(chat_id=user.chat_id, 
            message_id=message_id, reply_markup = reply_markup)

        # Count event attendees except current user
        num_attendees = len(self.get_event_attendees(event)) - 1

        context.bot.send_message(chat_id=user.chat_id, text = responses.EVENT_GOING.format(num_attendees, event.name))

    def event_not_going(self, context, user: User, event: Event, message_id):
        # Remove if was previously going
        if (event.id in user.events):
            user.events.remove(event.id)
        
        self.db_driver.update_user(user)

        self.logger.info(logging_settings.EVENT_NOT_GOING.format(user.display_name, user.id, event.id))
        
        # Change reply markup to reflect the change
        location_button = InlineKeyboardButton("Location",
                callback_data="event_location_" + event.id)
        keyboard = [[InlineKeyboardButton("Going!", 
                    callback_data = 'event_going_' + event.id)],
                    [location_button]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.edit_message_reply_markup(chat_id=user.chat_id, 
            message_id=message_id, reply_markup = reply_markup)

        # Count event attendees
        num_attendees = len(self.get_event_attendees(event))
        
        context.bot.send_message(chat_id=user.chat_id, text = responses.EVENT_NOT_GOING.format(num_attendees, event.name))

    def show_event_location(self, context, user: User, event: Event):
        if (not user.fields.get('location', None)):
            context.bot.send_message(chat_id=user.chat_id, text = responses.NO_LOCATION_RECORD)
            return
        
        # If location exists
        try:
            location = event.find_location(user_location=user.fields.get('location', None))
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)

        context.bot.send_message(chat_id=user.chat_id, text = responses.LOCATION_FOR_EVENT.format(event.name))
        context.bot.send_location(chat_id=user.chat_id, latitude=location['lat'], longitude=location['lng'])

    def show_event(self, context, event: Event, user: User, chat_id):
        # Add location keyboard button
        location_button = InlineKeyboardButton("Location",
                callback_data="event_location_" + event.id)
            
        # If user is admin, allow to notify or disable an event
        if (user.admin):
            keyboard = [[InlineKeyboardButton("Notify!", 
                    callback_data='event_notify_' + event.id)],
                    [InlineKeyboardButton("Attendees",
                    callback_data='event_attendees_' + event.id)],
                    [InlineKeyboardButton("Disable",
                    callback_data='event_disable_' + event.id)],
                    [location_button]]
            reply_markup = InlineKeyboardMarkup(keyboard)

        # If regular user and not going, allow to mark as going
        if ((not user.admin) and (event.id not in user.events)):
            keyboard = [[InlineKeyboardButton("Going!", 
                    callback_data = 'event_going_' + event.id)],
                    [location_button]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        # If going, allow to unmark
        if ((not user.admin) and (event.id in user.events)):
            keyboard = [[InlineKeyboardButton("I changed my mind", 
                    callback_data = 'event_not_going_' + event.id)],
                    [location_button]]
            reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(chat_id=chat_id, 
            text = event.format(), 
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup)

    def command_list_events(self, update, context):
        user_id = update.message.from_user.id
        user = self.db_driver.get_user(user_id)

        if (user is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_REGISTERED)
            return    

        events = self.db_driver.get_ongoing_events()

        if not events:
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NO_ONGOING_EVENTS)
            self.logger.info(logging_settings.EVENT_NO_ONGOING.format(user.display_name, user.id))
            return

        context.bot.send_message(chat_id=update.message.chat_id, text = responses.CURRENT_EVENTS)

        for event in events:
            self.show_event(context, event, user, update.message.chat_id)

        self.logger.info(logging_settings.EVENT_ONGOING.format(user.display_name, user.id, len(events)))

    def command_grant_location(self, update, context):
        location_keyboard = [
            [KeyboardButton(text="Share location", request_location=True)],
            [KeyboardButton(text="/cancel")]
        ]
        reply_markup = ReplyKeyboardMarkup(location_keyboard)
        context.bot.send_message(chat_id=update.message.chat_id, 
               text=responses.LOCATION_REQUEST, 
               reply_markup=reply_markup)

    # Location handler
    
    def handle_location(self, update, context):
        user_id = update.message.from_user.id
        user = self.db_driver.get_user(user_id)

        if (user is None):
            context.bot.send_message(chat_id=update.message.chat_id, text = responses.NOT_REGISTERED)
            return    

        reply_markup = ReplyKeyboardRemove()
        context.bot.send_message(chat_id=update.message.chat_id, text=responses.LOCATION_RECEIVED, reply_markup=reply_markup)
        self.logger.info(logging_settings.LOCATION_RECEIVED.format(user.display_name, user.id))
        
        # save user location
        user.fields['location'] = f"{update.message.location.latitude}, {update.message.location.longitude}"
        self.db_driver.update_user(user)


    # Error handlers

    def error_callback(self, bot, update, error):
        try:
            raise error
        except TelegramError as e:
            print(e)

    # Helper/auxillary functions

    def get_event_attendees(self, event: Event):
        users = self.db_driver.get_all_users()
        attendees = [user for user in users if (event.id) in user.events]
        return attendees

    def new_member_notify(self, context, user: User):
        users = self.db_driver.get_all_users()
        # remove self
        # users.remove(user)

        for u in users:
            context.bot.send_message(chat_id=u.chat_id, text = responses.NEW_USER_JOINED.format(user.display_name))

if __name__ == "__main__":
    try:
        RusMafiaBot(settings.token).start(clean=True)
    except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)