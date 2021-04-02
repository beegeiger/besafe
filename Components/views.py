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

from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from auth import requires_auth

views_bp = Blueprint('views_bp', __name__, template_folder='../templates',
    static_folder='../static')

@views_bp.route("/", methods=["GET"])
def go_home():
    """Renders the besafe homepage. (Tested)"""
    return render_template("homepage.html")

@views_bp.route('/dashboard', methods=["GET"])
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

@views_bp.route("/edit_profile", methods=["GET"])
@requires_auth
def edit_page():
    """Renders the Profile page"""

    #Queries User
    user = User.query.filter_by(email=session['current_user']).one()

    #Returns the Profile Template
    return render_template("edit_profile.html", user=user)    

@views_bp.route("/bs_alerts", methods=["GET"])
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

@views_bp.route("/sw_getting_started", methods=["GET"])
def get_started():
    """Renders the 'Getting Started with besafe' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    con_length = len(contacts)

    return render_template("getting_started_besafe.html", contacts=contacts, con_length=con_length, timezone=user.timezone)

@views_bp.route("/sched_alerts", methods=["GET"])
def scheduled_alerts():
    """Renders the 'Edit a Scheduled Alert-Set' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    return render_template("edit_sched_alerts.html", contacts=contacts, timezone=user.timezone)

@views_bp.route("/contacts", methods=["GET"])
@requires_auth
def user_contacts():
    """Renders the User's 'contacts' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    return render_template("contacts.html", contacts=contacts, timezone=user.timezone)

@views_bp.route("/check_ins", methods=["GET"])
@requires_auth
def checkin_page():
    """Renders the User's check-in page"""

    #The current user and check-ins are queried and the page is rendered
    user = User.query.filter_by(email=session['current_user']).one()
    check_ins = CheckIn.query.filter_by(user_id=user.user_id).all()
    return render_template("checkins_page.html", check_ins=check_ins, timezone=user.timezone)

@views_bp.route("/edit_recset/<alert_set_id>", methods=["GET"])
def edit_recset_page(alert_set_id):
    """Renders the page to edit a recurring alert set"""

    #Queries the user, alert_set, user's contacts, and associated alerts
    user = User.query.filter_by(email=session['current_user']).one()
    print("Edit Recset Path with alert_set_id: ", alert_set_id)
    print(AlertSet.query.filter_by(alert_set_id=alert_set_id).all())
    alert_set = AlertSet.query.filter_by(alert_set_id=alert_set_id).first()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    alert = Alert.query.filter_by(alert_set_id=alert_set_id).first()
    print(Alert.query.filter_by(alert_set_id=alert_set_id).all())

    return render_template("edit_rec_alerts.html", alert_set=alert_set, contacts=contacts, alert=alert, timezone=user.timezone)

@views_bp.route("/edit_schedset/<alert_set_id>", methods=["GET"])
def edit_schedset_page(alert_set_id):
    """Renders the page to edit a recurring alert set"""

    #Queries the user, alert_set, user's contacts, and associated alerts
    user = User.query.filter_by(email=session['current_user']).one()
    print("Edit Schedset Path with alert_set_id: ", alert_set_id)
    print(AlertSet.query.filter_by(alert_set_id=alert_set_id).all())
    alert_set = AlertSet.query.filter_by(alert_set_id=alert_set_id).first()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    alert = Alert.query.filter_by(alert_set_id=alert_set_id).first()
    print(Alert.query.filter_by(alert_set_id=alert_set_id).all())

    return render_template("edit_sched_alerts.html", alert_set=alert_set, contacts=contacts, alert=alert, timezone=user.timezone)

@views_bp.route("/map")
def get_map():
    """Renders User Map Page"""
    return render_template("map_page.html")