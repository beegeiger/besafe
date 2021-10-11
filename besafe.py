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
                   session, jsonify, Blueprint, url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (update, asc, desc)
from model import User, Contact, AlertSet, Alert, CheckIn, ReqCheck, connect_to_db, db
import requests
import logging

from auth import requires_auth
from functools import wraps
from os import environ as env
# from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from Components.alerts import alerts_bp
from Components.contacts import contacts_bp
from Components.profile import profile_bp
from Components.views import views_bp
from Components.location import location_bp
from Components.incoming import incoming_bp
from Components.check_ins import check_ins_bp
from Components.helpers import (check_in, create_alert, send_alert_contacts,
                    send_alert_user, check_alerts)
from secrets import oauth_client_secret, oauth_client_id, google_maps_key

app = Flask(__name__)
app.register_blueprint(views_bp)
app.register_blueprint(check_ins_bp)
app.register_blueprint(location_bp)
app.register_blueprint(incoming_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(profile_bp)

app.register_blueprint(alerts_bp)


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

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture'],
        'email': userinfo['email']
    }

    #Sets the 'current_user' value in the session to the user's e-mail
    session['current_user'] = userinfo['email']
    print("Session: ", session)

    #User Table is Queried to see if User already exists in dB
    user = User.query.filter_by(email=userinfo['email']).all()
    print("Callback User1: ", user)
    
    #If the user isn't in the dBase, they are added
    if user == []:
        new_user = User(name=userinfo['name'], email=userinfo['email'], username=userinfo['nickname'], fname=userinfo['given_name'], lname=userinfo['family_name'], created_at=datetime.datetime.now())
        db.session.add(new_user)
        db.session.commit()
        print("Callback NewUser: ", new_user)
        return redirect('/edit_profile')
    
    #The dBase changes are committed
    db.session.commit()

    #Redirects to the User Profile
    return redirect('/dashboard')

@app.route("/login/<special>", methods=["GET"])
def log_in(special=""):
    """Render's the log-in page if user not in session,
     otherwise redirects to the homepage (Still Works as of 1/21)"""
    print('login visited')
    if special == "development":
        session['current_user'] = 'developer@placeholder.com'
        user = User.query.filter_by(email='developer@placeholder.com).all()
        if user == []:
          new_user = User(name='dev', email='developer@placeholder.com', username='dev', fname='Dev', lname='Eveloper', created_at=datetime.datetime.now())
          db.session.add(new_user)
        db.session.commit()
        print("Callback NewUser: ", new_user)
        return redirect('/edit_profile')
    uri = "https://besafe.ngrok.io/callback"
    print(type(uri))
    return auth0.authorize_redirect(redirect_uri=uri, audience='https://dev-54k5g1jc.auth0.com/api/v2/')

@app.route("/logout")
def logout():
    """Logs user out and deletes them from the session (Tested)"""

    # Clear session stored data
    session.clear

    # Redirect user to logout endpoint
    params = {'returnTo': url_for('views_bp.go_home', _external=True), 'client_id': '78rUTjeVusqU3vYXyvNpOQiF8jEacf55'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
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
