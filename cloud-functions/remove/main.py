from helpers import get_monday, format_date
from secrets import get_secret

from google.cloud import datastore
import sentry_sdk
from sentry_sdk.integrations.serverless import serverless_function

kind = "Timetable"

sentry_url = get_secret("SENTRY_URL")
configcat_key = get_secret("CONFIGCAT_KEY")

sentry_sdk.init(sentry_url)
with sentry_sdk.configure_scope() as scope:
    scope.set_tag("service", "remove")

client = datastore.Client()

@serverless_function
def remove_timetable(data, context):
    date = format_date(get_monday())
    key = client.key(kind, date)

    query = client.query(kind=kind)
    query.add_filter('__key__', '<', key)
    query.keys_only()
    results = query.fetch()

    for entity in results:
        client.delete(entity.key)

    print('Removed timetables successfully')
    return