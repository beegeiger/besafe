import flask
from flask_debug import Debug
import math
import time
import json
import random
import string
import datetime
import threading
from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify, Blueprint)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (update, asc, desc)
from model import User, Contact, AlertSet, Alert, CheckIn, ReqCheck, connect_to_db, db
import requests
import logging
from views import views_bp
from auth import requires_auth
from functools import wraps
from os import environ as env
# from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from Components.alerts.alert_sets import alert_set_bp
from Components.alerts.alerts_rec import alerts_rec_bp
from Components.alerts.alerts_sched import alerts_sched_bp
from Components.contacts import contacts_bp
from Components.profile import profile_bp
from Components.location import location_bp
from Components.incoming import incoming_bp
from Components.check_ins import check_ins_bp
from Components.helpers import (check_in, create_alert, send_alert_contacts,
                    send_alert_user, check_alerts)
from secrets import oauth_client_secret, oauth_client_id, google_maps_key

app = Flask(__name__)
app.register_blueprint(views_bp, alert_sets_bp, alerts_sched_bp,
                     alerts_rec_bp, profile_bp, contact_bp, 
                     incoming_bp, location_bp, check_ins_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///besafe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy()
db.app = app

db.init_app(app)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Causes error messages for undefined variables in jinja
app.jinja_env.undefined = StrictUndefined

################################################################
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=oauth_client_id,
    client_secret=oauth_client_secret,
    api_base_url='https://dev-54k5g1jc.auth0.com',
    access_token_url='https://dev-54k5g1jc.auth0.com/oauth/token',
    authorize_url='https://dev-54k5g1jc.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

################################################################

if __name__ == "__main__":
    # start_runner()
    print("should be working")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config.from_object('configurations.DevelopmentConfig')
    # connect_to_db(app, 'postgresql:///besafe')
    print("Connected to DB.")
    Debug(app)
    app.run(debug=True, port=3600)
    app.run()
