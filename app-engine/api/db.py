from google.cloud import datastore

client = datastore.Client()

def handle_single(workday: str):
    key = client.key('Timetable', workday)
    response = client.get(key)
    if response is None:
        return {}
        
    return response