from besafe import app
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
                   session, jsonify)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (update, asc, desc)
from model import User, Contact, AlertSet, Alert, CheckIn, ReqCheck, connect_to_db, db
import requests
import logging


from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

from secrets import oauth_client_secret, oauth_client_id, google_maps_key
from auth import requires_auth

@app.route("/", methods=["GET"])
def go_home():
    """Renders the besafe homepage. (Tested)"""
    return render_template("homepage.html")

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

@app.route("/edit_profile", methods=["GET"])
@requires_auth
def edit_page():
    """Renders the Profile page"""

    #Queries User
    user = User.query.filter_by(email=session['current_user']).one()

    #Returns the Profile Template
    return render_template("edit_profile.html", user=user)    

@app.route("/bs_alerts", methods=["GET"])
@requires_auth
def besafe_alerts():
    """Renders the main besafe page including a user's alert-sets"""

    #Creates variables for the curent time, date, and datetime for convenience
    time = datetime.datetime.now().time()
    date = (datetime.datetime.today())
    now = datetime.datetime.now()

    #Queries the dBase for the current user and their alerts and contacts
    if 'current_user' in session:
        user = User.query.filter_by(email=session['current_user']).one()
    else:
        return redirect('/login')

    #Queries Alert Sets, Alerts, Contacts and creates and empty list for the alert sets
    alert_sets = AlertSet.query.filter_by(user_id=user.user_id).all()
    al_sets = []
    alerts = Alert.query.filter_by(user_id=user.user_id).all()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    con_length = len(contacts)

    #If the user has added no contacts, they are re-routed to the 'getting started' page
    if con_length < 1:
        return redirect("/contacts")

    #Loops through all user's alert-sets and initiates variables to keep track of them
    for a_set in alert_sets:

        aset_alerts = []
        a_set.total = 0

        #Loops through the alerts and adds the datetime for each to the aset_alerts list
        for alert in alerts:
            if alert.active == False:
                if a_set.alert_set_id == alert.alert_set_id and a_set.interval and alert.active == False:
                    tim = now + datetime.timedelta(minutes=a_set.interval)
                    aset_alerts.append(tim)

                elif a_set.alert_set_id == alert.alert_set_id and a_set.interval and alert.active == True:
                    aset_alerts.append(alert.datetime)

                elif a_set.alert_set_id == alert.alert_set_id and alert.active == True:
                    dtime = alert.datetime
                    aset_alerts.append(dtime)
                elif a_set.alert_set_id == alert.alert_set_id and alert.active == False:
                    dtime = datetime.datetime.combine(date, alert.time)
                    aset_alerts.append(dtime)

        """If there is at least one alert for each alert-set, the earliest alert and
        the total number of seconds until that alert are saved to the alert-set object"""
        if len(aset_alerts) >= 1:
            if aset_alerts[0] != []:

                aset_alerts.sort()

                a_set.next_alarm = aset_alerts[0]
                a_set.next_alarm_dis = aset_alerts[0].strftime("%I:%M %p, %m/%d/%Y")
                d1 = now - aset_alerts[0]

                d2 = abs(d1.total_seconds())

                a_set.total =int(d2)


            else:
                a_set.next_alarm_dis = now.strftime("%I:%M %p, %m/%d/%Y")

        #If there are no alerts, the current datetime is used as a placeholder
        else:a_set.next_alarm_dis = now.strftime("%I:%M %p, %m/%d/%Y")

    for a_s in alert_sets:
        if len(a_s.a_name) > 14:
            a_s.a_name = a_s.a_name[:9] + "..." + a_s.a_name[-4:]


    return render_template("besafe_alerts.html", alert_sets=alert_sets, alerts=alerts, timezone=user.timezone, user=user, contacts=contacts)

@app.route("/sw_getting_started", methods=["GET"])
def get_started():
    """Renders the 'Getting Started with besafe' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    con_length = len(contacts)

    return render_template("getting_started_besafe.html", contacts=contacts, con_length=con_length, timezone=user.timezone)

@app.route("/sched_alerts", methods=["GET"])
def scheduled_alerts():
    """Renders the 'Create a Scheduled Alert-Set' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    return render_template("scheduled_alerts.html", contacts=contacts, timezone=user.timezone)    