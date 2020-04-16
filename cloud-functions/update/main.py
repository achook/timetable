from librus import get_timetables, format_date, get_monday, LibrusNotAvailible
from secrets import get_secret
from config import get_config

from google.cloud import datastore
import sentry_sdk
from sentry_sdk.integrations.serverless import serverless_function

sentry_url = get_secret("SENTRY_URL")

sentry_sdk.init(sentry_url)
with sentry_sdk.configure_scope() as scope:
    scope.set_tag('service', 'update')

username = get_config('USERNAME')
password = get_config('PASSWORD')

kind = 'Timetable'
client = datastore.Client()

@serverless_function
def update_timetable(data, context):
    timetables = None

    try:
        timetables = get_timetables(username, password, 4)
    except LibrusNotAvailible as err:
        print(f'An error occured when connecting to Librus: {err}')
        return
    
    entities = []

    for element in timetables:
        key = client.key(kind, element.date)
        entity = datastore.Entity(key=key)
        
        del(element.date)
        entity.update(vars(element))
        
        entities.append(entity)

    client.put_multi(entities)

    print('Added timetables successfully')
    return