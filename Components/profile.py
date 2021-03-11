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

from auth import requires_auth
from functools import wraps
from os import environ as env
from dotenv import load_dotenv, find_dotenv

from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode


profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/callback')
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

    #User Table is Queried to see if User already exists in dB
    user = User.query.filter_by(email=userinfo['email']).all()
    
    #If the user isn't in the dBase, they are added
    if user == []:
        new_user = User(name=userinfo['name'], email=userinfo['email'], username=userinfo['nickname'], fname=userinfo['given_name'], lname=userinfo['family_name'], created_at=datetime.datetime.now())
        db.session.add(new_user)
    
    #The dBase changes are committed
    db.session.commit()

    #Redirects to the User Profile
    return redirect('/dashboard')

@profile_bp.route("/login", methods=["GET"])
def log_in():
    """Render's the log-in page if user not in session,
     otherwise redirects to the homepage (Still Works as of 1/21)"""
    print('login visited')

    uri = "https://besafe.ngrok.io/callback"
    print(type(uri))
    return auth0.authorize_redirect(redirect_uri=uri, audience='https://dev-54k5g1jc.auth0.com/api/v2/')

@profile_bp.route("/logout")
def logout():
    """Logs user out and deletes them from the session (Tested)"""

    # Clear session stored data
    session.clear

    # Redirect user to logout endpoint
    params = {'returnTo': url_for('go_home', _external=True), 'client_id': '78rUTjeVusqU3vYXyvNpOQiF8jEacf55'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@profile_bp.route("/edit_profile", methods=["POST"])
def edit_profile():
    """Submits the profile edits"""


    #Gets info from html form and dbase
    email_input = request.form['email_input']
    fname = request.form['fname']
    lname = request.form['lname']
    phone = request.form['phone']
    timezone = request.form['tzim']

    #Queries User
    user = User.query.filter_by(email=session['current_user']).one()

    #Updates User Object in DB and Commits
    (db.session.query(User).filter(
        User.email == session['current_user']).update(
            {'fname': fname, 'lname': lname, 'email': email_input,
                'phone': phone,'timezone': timezone}))
    db.session.commit()
    
    flash('Your Profile was Updated!')
    
    #Refreshes the Profile Page
    return redirect("/edit_profile")

@profile_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """Using POST, feedback is added from the check-in page"""

    #Get's the Feedback details from the form on the page and adds it to the dBase
    text = request.form['feedback_text']
    user = User.query.filter_by(email=session['current_user']).one()
    dt = datetime.datetime.now()
    new_feedback = Feedback(user_id=user.user_id, datetime=dt, content=text)
    db.session.add(new_feedback)
    db.session.commit()
    return "Feedback Submitted!"

@profile_bp.route("/user_code", methods=["POST"])
def new_user_code():
    """Creates a new User Code"""
    
    user = User.query.filter_by(email=session['current_user']).one()
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    # code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code_check = User.query.filter_by(user_code=code).all()
    while len(code_check) > 0 or "0" in code or "O" in code:
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        # code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        code_check = User.query.filter_by(user_code=code).all()

    db.session.query(User).filter_by(user_id=user.user_id).update({'user_code': code})

    db.session.commit()

    return str(code)