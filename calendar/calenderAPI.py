import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from openai import OpenAI
import json

# Enable Google Calendar API
# Create OAuth

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# client = OpenAI(
#     # api_key = "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"
# )

def giveOutput():
  creds = None

  if os.path.exists("calendarToken.json"):
    creds = Credentials.from_authorized_user_file("calendarToken.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)

    with open("calendarToken.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.now().isoformat() + "Z"

    events_result = service.events().list(calendarId = "primary", timeMin = now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    for event in events:
      start = event['start'].get('dateTime', event['start'].get("date"))
      end = event['end'].get('dateTime', event['end'].get("date"))
      print(start, end, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")

def needInput(text):
  now = datetime.now()

  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are google calendar, format the information inputted to be like this {'summary: title', 'start: {dateTime, timeZone}', 'end: {dateTime, timeZone'}}. If no end time is given, give an approximation on how long you think it will take and make end time equal to start time plus that approximation. For timezone, it will always be America/Toronto. Give the date and time in RCF 3339 format."},
      {"role": "user", "content": text + " and the current date is " + now.strftime("%B %d, %Y") + " and the current time is " + now.strftime("%H:%M")}
    ]
  )
  json_object = json.loads(completion.choices[0].message.content.replace("'", '"'))
  createEvent(json_object)

def createEvent(event):
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Adds events to the calendar
    event = service.events().insert(calendarId = 'primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
  
  except HttpError as error:
    print(f"An error occurred: {error}")