from pymongo import MongoClient
import settings
import logging
import constants.logging as logging_settings
from models.user import User
from models.event import Event

class MongoDriver:
    def __init__(self, connection_string):
        self.setup_logging()
        
        self.client = MongoClient(connection_string)
        self.db     = self.client.rusmafia

        # extract collections
        self.events = self.db.events
        self.users  = self.db.users

    def setup_logging(self):
        self.logger = logging.getLogger('db')
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

    def add_user(self, user: User):
        # make sure not to add the same user twice
        result = self.users.update_one({u'id': user.id}, {'$set': user.to_json()})

        if result.matched_count > 0:
            self.logger.info(logging_settings.DB_USER_UPDATED.format(user.display_name, user.id))
            # user already existed
            return False
        else:
            # new user
            self.users.insert_one(user.to_json())
            self.logger.info(logging_settings.DB_USER_ADDED.format(user.display_name, user.id))
            return True

    def update_user(self, user: User):
        result = self.users.update_one({u'id': user.id}, {'$set': user.to_json()})

        if result.matched_count > 0:
            self.logger.info(logging_settings.DB_USER_UPDATED.format(user.display_name, user.id))
        else:
            self.logger.info(logging_settings.DB_USER_NOT_FOUND.format(user.id))

    def get_user(self, user_id):
        result = self.users.find_one({'id': user_id})
        if not result:
            self.logger.info(logging_settings.DB_USER_NOT_FOUND.format(user_id))
            return None
        
        del result['_id']
        # Wrap result in a user class
        return User(**result)

    def remove_user(self, user: User):
        result = self.users.delete_one({u'id': user.id})

        if result.matched_count > 0:
            self.logger.info(logging_settings.DB_USER_DELETED.format(user.display_name, user.id))
        else:
            self.logger.info(logging_settings.DB_USER_NOT_FOUND.format(user.id))
    
    def get_all_users(self):
        result = list(self.users.find({}))
        # delete all id fields
        for u in result:
            del u['_id']
        
        return [User(**u) for u in result]
    

    def add_event(self, event: Event):
        # make sure not to add the same event twice
        result = self.events.update_one({u'id': event.id}, {'$set': event.to_json()})

        if result.matched_count > 0:
            self.logger.info(logging_settings.DB_EVENT_UPDATED.format(event.name, event.id))
        else:
            self.events.insert_one(event.to_json())
            self.logger.info(logging_settings.DB_EVENT_ADDED.format(event.name, event.id))
        
    def get_event(self, event_id):
        result = self.events.find_one({'id': event_id})
        if not result:
            self.logger.info(logging_settings.DB_EVENT_NOT_FOUND.format(event_id))
            return None
        
        del result['_id']
        # Wrap result in a user class
        return Event(**result)
    
    def update_event(self, event: Event):
        result = self.events.update_one({u'id': event.id}, {'$set': event.to_json()})

        if result.matched_count > 0:
            self.logger.info(logging_settings.DB_EVENT_UPDATED.format(event.name, event.id))
        else:
            self.logger.info(logging_settings.DB_EVENT_NOT_FOUND.format(event.id))

    def get_ongoing_events(self):
        result = list(self.events.find({'ongoing': True}))
        # delete all id fields
        for e in result:
            del e['_id']

        return [Event(**e) for e in result]
