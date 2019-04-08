import uuid
import constants.responses as responses
from google_maps import GoogleMapsAPI
from datetime import datetime, timedelta
import settings

class Event:
    def __init__(self, id = None, name = None, time = None, 
                    location = None, description = None, 
                    ongoing = True, organizer = None, **kwargs):
        # generate id if not specified

        self.id = id

        if id is None:
            self.id = str(uuid.uuid4())

        self.name = name
        self.time = time
        self.location = location
        self.description = description
        self.ongoing = ongoing
        self.organizer = organizer

        self.fields = {}

        # Allow for arbitrary fields
        for key, value in kwargs.items():
            self.fields[key] = value
    
    def to_json(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'time': self.time,
            'location': self.location,
            'description': self.description,
            'ongoing': self.ongoing,
            'organizer_id': self.organizer
        }
        obj.update(self.fields)
        return obj

    def get_utc_time(self):
        start = datetime.strptime(self.time, settings.time_format)
        end = start + timedelta(hours=2)
        return (start.isoformat(), end.isoformat())

    def format_google_calendar(self):
        (start, end) = self.get_utc_time()
        return {
            'summary': self.name,
            'location': self.location,
            'description': self.description,
            'start': {
                'dateTime': start,
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'America/Los_Angeles',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
                ],
            }
        }

    def format(self):
        return responses.EVENT.format(
            self.name,
            self.time,
            self.location,
            self.description,
            self.fields.get('google_calendar_url', ''),
            self.organizer
        )

    def find_location(self, user_location):
        gmaps = GoogleMapsAPI(settings.google_maps_key)
        return gmaps.find_place_nearby(user_location, self.location)
        
