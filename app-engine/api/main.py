from db import handle_single
from secrets import get_secret

from flask import Flask, request, jsonify
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_url = get_secret('SENTRY_URL')
sentry_sdk.init(sentry_url, integrations=[FlaskIntegration()])
with sentry_sdk.configure_scope() as scope:
    scope.set_tag('service', 'api')

app = Flask(__name__)

@app.route('/single')
def single():
    date = request.args['date']
    resp = handle_single(date)
    return jsonify(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)