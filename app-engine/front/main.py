from secrets import get_secret
from helpers import get_timetable, display_date, is_night

from flask import Flask, render_template
import sentry_sdk

sentry_url = get_secret('SENTRY_URL')
sentry_sdk.init(sentry_url)
with sentry_sdk.configure_scope() as scope:
    scope.set_tag('service', 'front')

app = Flask(__name__)

@app.route('/')
def root():
    response = get_timetable()
    date = response['date']
    
    timetable = response['timetable']
    classes = []
    time = 'Nie ma lekcji 👍'

    if timetable and timetable['beginning']:
        classes = timetable['classes']
        time = f'{timetable['beginning']} - {timetable['end']}' 

    dark = is_night()
    
    return render_template('index.html', classes=classes, date=date, time=time, dark=dark)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
