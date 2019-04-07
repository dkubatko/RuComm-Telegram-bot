from __future__ import print_function
from datetime import datetime  
from datetime import timedelta
import pickle
import os.path
import settings
from models.event import Event
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleCalendarAPI:
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_calendar(self):
        calendar = self.service.calendars().get(calendarId='primary').execute()
        return calendar

    def create_event(self, event: Event):
        event = self.service.events().insert(calendarId='primary', body=event.format_google_calendar()).execute()
        # extract unique event id from the link
        eid = event.get('htmlLink').split('eid=')[1]
        return settings.google_share_link_format.format(eid)