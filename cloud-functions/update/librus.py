from config import get_config

import requests
import datetime
import json

REDIRECT_URL = 'http://localhost/bar'
LOGIN_URL = 'https://portal.librus.pl/rodzina/login/action'
OAUTH_URL = 'https://portal.librus.pl/oauth2/access_token'
SYNERGIA_URL = 'https://portal.librus.pl/api/v2/SynergiaAccounts'
FRESH_URL = 'https://portal.librus.pl/api/SynergiaAccounts/fresh/{login}'


class Week:
    def __init__(self, i: int):
        monday = get_nth_monday(i)
        self.monday = format_date(monday)
        self.days = []
        for j in range(0, 5):
            day = monday + datetime.timedelta(days=j)
            self.days.append(format_date(day))


class Timetable:
    def __init__(self, date = None):
        self.date: str = date
        self.beginning: str = None
        self.end: str = None
        self.classes = []

    def add_class(self, name: str, teacher: str, beginning: str, end: str, classroom: str, is_substitution: bool = False, is_canceled: bool = False):
        self.classes.append({
            'name': name,
            'teacher': teacher,
            'classroom': classroom,
            'beginning': beginning,
            'end': end,
            'is_substitution': is_substitution,
            'is_canceled': is_canceled
        })

class LibrusNotAvailible(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

def get_token(username: str, password: str) -> str:
    """
    Get authorization token

    Params:
        username (str): Librus username
        password (str): user password

    Returns:
        str: Token returned by server
    """

    auth_session = requests.session()

    client_id = get_config('LIBRUS_CLIENT_ID')
    librus_login_url = f'https://portal.librus.pl/oauth2/authorize?client_id={client_id}&redirect_uri={REDIRECT_URL}&response_type=code'
    csrf_sess = auth_session.get(librus_login_url)
    if csrf_sess.status_code != 200:
        raise LibrusNotAvailible(f'Unable to get csrf token, server responded with {csrf_sess.status_code}')

    csrf_token = csrf_sess.text[
                 csrf_sess.text.find('name="csrf-token" content="') + 27:csrf_sess.text.find('name="csrf-token" content="') + 67
    ]

    login_response_redir = auth_session.post(
        LOGIN_URL,
        data=json.dumps({'email': username, 'password': password}),
        headers={'X-CSRF-TOKEN': csrf_token, 'Content-Type': 'application/json'}
    )
    if login_response_redir.status_code == 403:
        raise LibrusNotAvailible(login_response_redir.json()['errors'][0])
    elif login_response_redir.status_code != 200:
        raise LibrusNotAvailible(f'Unable to get redir url, server responded with {login_response_redir.status_code}')

    redir_addr = login_response_redir.json()['redirect']
    
    access_code_sess = auth_session.get(redir_addr, allow_redirects=False)
    if access_code_sess.status_code != 302:
        raise LibrusNotAvailible(f'Unable to get access code, server responded with {access_code_sess.status_code} instead of 302')
    access_code = access_code_sess.headers['location'][26:]

    token_sess = auth_session.post(
        OAUTH_URL,
        data={
            'grant_type': 'authorization_code',
            'code': access_code,
            'client_id': client_id,
            'redirect_uri': REDIRECT_URL
        }
    )
    if token_sess.status_code != 200:
        raise LibrusNotAvailible(f'Unable to get access token, server responded with {token_sess.status_code}')

    synergia_token = token_sess.json()['access_token']

    accounts_sess = auth_session.get(
                    SYNERGIA_URL,
                    headers={'Authorization': f'Bearer {synergia_token}'}
    )
    
    if accounts_sess.status_code != 200:
        raise LibrusNotAvailible(f'Unable to get accounts, server responded with {accounts_sess.status_code}')

    account = accounts_sess.json()['accounts'][0]

    return account["accessToken"]

def get_classrooms(token: str):
    """
    Get dict mapping api classrooms ids to actual names

    Returns:
        dict: mapping ids to names
    """
    headers = {
        'Authorization': 'Bearer ' + token
    }

    # Request URL
    url = 'https://api.librus.pl/2.0/Classrooms'

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise LibrusNotAvailible(f'Unable to get classrooms, server responded with {r.status_code}')

    raw_classrooms = r.json()['Classrooms']

    classroom_map = {}

    for classroom in raw_classrooms:
        classroom_map[classroom['Id']] = classroom['Name']

    return classroom_map   


# Get raw JSON timetable
def get_raw_timetable(token: str, monday: str):
    """
    Get raw JSON timetable from server

    Params:
        token (str): Access token, acquired using get_token function
        monday (str) - optional: Monday, on which the week, for which you want to get timetable, begins; format -> 2018-01-02

    Returns:
        object: Server's properiaty formatted timetable

    """

    # Make the request header with obtained token
    headers = {
        'Authorization': 'Bearer ' + token
    }

    # Request URL
    url = 'https://api.librus.pl/2.0/Timetables'
    
    # If user specified monday - use it, if not let the server handle it
    if monday:
        url += '?weekStart='
        url += monday

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise LibrusNotAvailible(f'Unable to get timetable, server responded with {r.status_code}')

    return r.json()['Timetable']


def format_date(date) -> str:
    """
    Format date in server's format (eg. 2018-05-02)

    Params:
        date (datetime || date): object to format
    
    Returns:
        string: Formatted string
    """

    return date.strftime('%Y-%m-%d')


def get_monday() -> datetime.datetime:
    """
    Get nearest monday

    Returns:
        datetime.datetime: Nearest monday (with current hour)
    """

    # Check today's weekday and hour
    now = datetime.datetime.now()
    weekday = now.weekday()

    return now - datetime.timedelta(days=weekday)

def get_nth_monday(n: int) -> datetime.datetime:
    """
    Get nth monday

    Returns:
        datetime.datetime: n-th monday (with current hour)
    """
    return get_monday() + datetime.timedelta(days=7*n)

def get_monday_array(length: int = 4) -> datetime.datetime:
    """
    Get array of mondays

    Returns:
        datetime.datetime[]: Array of (length) mondays with current hour
    """
    monday_array = []

    for i in range(length):
        monday = get_nth_monday(i)
        formatted = format_date(monday)
        monday_array.append(formatted)

    return monday_array      


def get_timetables(username: str, password: str, length: int) -> Timetable:
    """
    Get timetable for the nearest working day formatted as Timetable object

    Params:
        username (str): Librus username
        password (str): user password

    Returns:
        Timetable: timetable for the nearest working day
    """
    timetables = []

    weeks = []
    for i in range(0, length):
        weeks.append(Week(i))

    token = get_token(username, password)
    classrooms = get_classrooms(token)

    for week in weeks:
        raw_timetable = get_raw_timetable(token, week.monday)

        for day in week.days:
            tt = Timetable(day)

            for element in raw_timetable[day]:
                if not element:
                    continue

                subject_name = element[0]['Subject']['Name']
                teacher = f"{element[0]['Teacher']['FirstName']} {element[0]['Teacher']['LastName']}"

                is_substitution = element[0]['IsSubstitutionClass']
                is_canceled = element[0]['IsCanceled']

                beginning = element[0]['HourFrom']
                end = element[0]['HourTo']

                classroom = None
                if 'Classroom' in element[0]:
                    classroom_id = element[0]['Classroom']['Id']
                    classroom_id = int(classroom_id)
                    classroom = classrooms[classroom_id]

                tt.add_class(subject_name, teacher, beginning, end, classroom, is_substitution, is_canceled)

                if not is_canceled:
                    if not tt.beginning:
                        # Set beginning of the lessons time
                        tt.beginning = beginning

                    # Set end of the lessons time
                    tt.end = end

            timetables.append(tt)

    return timetables
