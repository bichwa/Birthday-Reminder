import json
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request

def load_credentials():
    # Load credentials from the JSON file
    with open('credentials.json') as f:
        credentials = json.load(f)
    return credentials

def authorize(credentials):
    # Set up OAuth 2.0 flow
    flow = InstalledAppFlow.from_client_config(credentials, ['https://www.googleapis.com/auth/calendar'])
    # Start the authorization flow
    return flow.run_local_server(port=0)

def create_service(credentials):
    # Create Google Calendar API service object
    return build('calendar', 'v3', credentials=credentials)

def fetch_facebook_birthdays(access_token):
    # Fetch user's birthdays from Facebook Graph API
    url = f'https://graph.facebook.com/me/friends?fields=birthday&access_token={access_token}'
    response = requests.get(url)
    data = response.json()
    return data.get('data', [])

def main():
    # Load credentials
    credentials = load_credentials()
    # Authorize with OAuth 2.0
    creds = authorize(credentials)
    # Create Google Calendar API service
    service = create_service(creds)
    
    # Fetch user's Facebook birthdays
    facebook_access_token = ''
    birthdays = fetch_facebook_birthdays(facebook_access_token)
    
    try:
        # Add each friend's birthday to Google Calendar
        for friend in birthdays:
            if 'birthday' in friend:
                # Create event in Google Calendar
                birthday_date = friend['birthday']
                summary = f"{friend['name']}'s Birthday"
                event = {
                    'summary': summary,
                    'start': {
                        'date': birthday_date,
                    },
                    'end': {
                        'date': birthday_date,
                    },
                    'reminders': {
                        'useDefault': False,
                    },
                }
                created_event = service.events().insert(calendarId='primary', body=event).execute()
                print('Event created: %s' % (created_event.get('htmlLink')))
    except RefreshError:
        # Handle token refresh
        creds.refresh(Request())
        main()

if __name__ == "__main__":
    main()
