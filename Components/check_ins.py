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
from model import User, Contact, Alert, CheckIn, ReqCheck, Location, connect_to_db, db
import requests
import logging
from Components.helpers import (check_in, create_alert, send_alert_contacts, send_alert_user, check_alerts, add_log_note, add_loc)
from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from auth import requires_auth

check_ins_bp = Blueprint('check_ins_bp', __name__)

@check_ins_bp.route("/add_check_in", methods=["POST"])
def add_new_checkin():
    """Using POST, a new check-in is added from the check-in page"""
    print("Request Form: ", request.form)
    #sets variable dt as equal to the current datetime
    dt = datetime.datetime.now()
    #Get's the check-in details from the form on the page and runs the check_in helper-function
    text = request.form['check_text']
    user = User.query.filter_by(email=session['current_user']).one()
    add_log_note(user.user_id, dt, "Check-In", text)
    #Use's the helper function check_in()
    check_in(user.user_id, text)

    #Queries the active and all alerts
    alerts = Alert.query.filter(Alert.user_id == user.user_id, Alert.active == True).all()
    all_alerts = Alert.query.filter(Alert.user_id == user.user_id).all()

    #Creates and empty list which is then filled with datetimes from the active alerts
    alert_datetimes = []
    for alert in alerts:
        if alert.datetime:
            alert_datetimes.append(alert.datetime)

    #The List of Datetimes is sorted
    alert_datetimes.sort()

    #If there is at least one active alert, a message is created with that info
    if len(alert_datetimes) > 0:
        diff = datetime.datetime.now() - alert_datetimes[0]
        minutes = (diff.total_seconds()) / 60
        time = alert_datetimes[0].time()
        check_time = (alert_datetimes[0] - datetime.timedelta(hours=1)).time()
        message = "Your Check-In has been received! Your next alarm is due in " + str(minutes) + " minutedt = datetime.datetime.now()s, so you must check in between " + str(check_time) + " and " + str(time) + "."

    #Otherwise a message is created explaining that there are no active alerts
    else:
        message = "Your check-in has been received! You don't have any alerts currently active."

    #The message is then sent back to the user as confirmation
    # if len(all_alerts) > 0:
    #     send_alert_user(all_alerts[0].alert_id, message)

    return redirect("/check_ins")

@check_ins_bp.route("/add_location", methods=["POST"])
def add_new_location():
    lat = request.form['lat']
    long = request.form['long']
    user = User.query.filter_by(email=session['current_user']).one()
    dt = datetime.datetime.now()
    add_loc(user.user_id, lat, long, dt)
    return "New Location Added"
