from datetime import datetime, date, timedelta, time
from pytz import timezone
from google.cloud import datastore

client = datastore.Client()

tz = timezone('Europe/Warsaw')

def format_date(d):
    return d.strftime('%Y-%m-%d')

def display_date(d):
    d = date.fromisoformat(d)
    return d.strftime('%d.%m')

def get_workday():
    now = datetime.now(tz=tz)
    workday = None

    if now.weekday() > 4:
        days_to_add = 2 - (now.weekday() % 5)
        workday = now.date() + timedelta(days=days_to_add)
        return format_date(workday)

    key = client.key('Timetable', format_date(now))
    response = client.get(key)
    raw_end_time = None

    if response is not None:
        raw_end_time = response['end']

    # if 'end' field in datastore is null, there are no lessons that day
    if raw_end_time is None:
        workday = now.date() + timedelta(days=1)
    else:
        end_hour, end_minute = raw_end_time.split(':')
        end_hour = int(end_hour)
        end_minute = int(end_minute)

        if (end_hour < now.hour or (end_hour == now.hour and end_minute < now.minute)):
            workday = now.date() + timedelta(days=1)
        else: 
            workday = now.date()

    if workday.weekday() == 5:
        workday = workday + timedelta(days=2)
    
    return format_date(workday)

def get_timetable():
    workday = get_workday()
    key = client.key('Timetable', workday)
    response = client.get(key)
    
    return {
        'date': display_date(workday),
        'timetable': response
    }

def is_night():
    now = datetime.now(tz=tz)
    hour = now.hour
    return (hour >= 22 or hour <= 5)