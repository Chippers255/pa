import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_summary():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        end_of_day = (datetime.datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat() + 'Z'
        
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              timeMax=end_of_day, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found for today.')
            return

        print('Your schedule for today:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event['summary']
            
            start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            print(f"\n{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}: {summary}")
            
            # Get attendees
            attendees = event.get('attendees', [])
            if attendees:
                print("Attendees:")
                for attendee in attendees:
                    print(f"- {attendee.get('email')}")
            
            # Get location
            location = event.get('location')
            if location:
                print(f"Location: {location}")
            
            # Get description
            description = event.get('description')
            if description:
                print(f"Description: {description}")
            
            # Get conference data (for video calls)
            conference_data = event.get('conferenceData')
            if conference_data:
                entry_points = conference_data.get('entryPoints', [])
                for entry in entry_points:
                    if entry.get('entryPointType') == 'video':
                        print(f"Video call link: {entry.get('uri')}")
                        break

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    get_calendar_summary()
