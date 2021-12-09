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
from model import User, Contact, Alert, CheckIn, ReqCheck, connect_to_db, db, User_log
import requests
import logging
from Components.helpers import (check_in, create_alert, send_alert_contacts, send_alert_user, check_alerts, add_log_note)
from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from auth import requires_auth

alerts_bp = Blueprint('alerts_bp', __name__)

@alerts_bp.route("/activate/<alert_id>")
def activate_alertset(alert_id):
    """Activates an alert set"""

    #The alert set in question is queried
    alert = Alert.query.filter_by(alert_id=alert_id).one()

    #Variables set to the current date, time, and datetime are created for convenience
    time = datetime.datetime.now().time()
    date = (datetime.datetime.today())
    dt = datetime.datetime.now()

    #An empty list is created to store the datetimes of the alerts associated with the alert set
    dt_list = []

    #If there is no start date, the start date is set to today
    if alert.date == None:
        db.session.query(Alert).filter_by(alert_id=alert_id).update({'date': date})

    #The alert datetime is updated added to the the alert datetime
    dtime = datetime.datetime.combine(date, alert.time)
    db.session.query(Alert).filter_by(alert_id=alert.alert_id).update({'datetime': dtime, 'active': True, 'status': "Active With No Check-Ins so Far"})
    dt_list.append(dtime)

    #The Variable "note" is created, which includes the text of the log entry
    note = "Check In " + str(alert.a_name) + " For " + str(alert.time.strftime("%I:%M %p")) + " Activated. "

    #If there is a message included in the alert, it is included in the log entry
    if alert.message:
        note += "The user included the following message: " + alert.message + "."

    #The log note is saved to the database
    add_log_note(alert.user_id, dt, "Activation", note, alert.message, alert.time)
    #Session is Commited
    db.session.commit()

    #The alert datetime list is sorted and the earliest time is then sent back to the page
    alarm_dt = dtime.strftime("%I:%M %p, %m/%d/%Y")
    return str(alarm_dt)

@alerts_bp.route("/deactivate/<alert_id>")
def deactivate_alertset(alert_id):
    """Deactivates an alert set"""

    #Today's Date and DateTime are set to variables
    date = datetime.date.today()
    dt_now = datetime.datetime.now()

    #The alert is queried and today's date is combined with the alert's time
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    dt = datetime.datetime.combine(date, alert.time)

    #The alert object is updated and session is commited
    db.session.query(Alert).filter_by(alert_id=alert.alert_id).update(
    {'active': False, 'checked_in': 0,'datetime': None, 'status': "Scheduled Alert has been Deactivated"})
    db.session.commit()

    #The Variable "note" is created, which includes the text of the log entry
    note = "Check In " + str(alert.a_name) + " For " + str(alert.time.strftime("%I:%M %p")) + " Deactivated" + "."

    #The log note is saved to the database
    add_log_note(alert.user_id, dt_now, "Deactivation", note, alert.message, alert.time)
    return redirect("/bs_alerts")

@alerts_bp.route("/add_alert", methods=["POST"])
def add_alert():
    """Adds an alert to the dBase"""
    #The user is queried along with all associated alerts
    user = User.query.filter_by(email=session['current_user']).one()
    alerts_all = Alert.query.filter_by(user_id=user.user_id).all()

    #Gets the alert and alert set info from the form on the add a new rec set page
    name = request.form['a_name']
    desc = request.form['descri']
    interval = request.form['interval']
    contacts = request.form.getlist('contact')
    time = request.form['time']

    #If there is no interval, the variable is set to None
    if interval == "":
        interval = None

    #If no name is included, the name is set as the next sequential number
    if len(name)== 0:
        name = "Alert " + str(len(alerts_all))

    #Current DateTime is queried
    dt = datetime.datetime.now()

    #Initiates 3 contact variables, sets the first to the first contact and the next two to None
    contact1 = int(contacts[0])
    contact2 = None
    contact3 = None

    #If more than one contact is associated with the alert set, the following variables are set to them
    if len(contacts) > 1:
        contact2 = int(contacts[1])
    if len(contacts) > 2:
        contact3 = int(contacts[2])

    #A new alert (associated with the alert set) is created, added, and commited to the dBase
    new_alert = Alert(user_id=user.user_id, contact_id1=contact1, a_name=name,
                      contact_id2=contact2, contact_id3=contact3, interval=interval, message=desc, time=time,
                      active=False, status='Not Yet Activated')

    db.session.add(new_alert)
    db.session.commit()

    #The new alert is now queried
    alert = Alert.query.filter_by(a_name=name).order_by(Alert.alert_id.desc()).first()

    #The Variable "note" is created, which includes the text of the log entry
    note = "Check In " + str(name) + " For " + str(alert.time.strftime("%I:%M %p")) + " Created. "

    #If there is a message included in the alert, it is included in the log entry
    if desc:
        note += "The user included the following message: " + str(desc) + "."
    add_log_note(user.user_id, dt, "Check-In Added", note, time)
    return redirect("/bs_alerts")


@alerts_bp.route("/save_alert/<alert_id>", methods=["POST"])
def save_alert(alert_id):
    """Saves the edits to a recurring alert set"""

    """Adds a recurring Alert-Set to the dBase"""
    user = User.query.filter_by(email=session['current_user']).one()
    alerts_all = Alert.query.filter_by(user_id=user.user_id).all()

    #Gets the alert and alert set info from the form on the add a new rec set page
    name = request.form['a_name']
    desc = request.form['descri']
    interval = request.form['interval']
    contacts = request.form.getlist('contact')
    time = request.form['time']
    print("name1: ", name, type(name), len(name))

    if len(name)== 0:
        name = "Alert " + str(len(alerts_all))
    print("name2: ", name, type(name), len(name))
    #Queries the current user

    dt = datetime.datetime.now()

    if time == "":
        time = None
    if interval == "":
        interval = None

    #Initiates 3 contact variables, sets the first to the first contact and the next two to None
    contact1 = int(contacts[0])
    contact2 = None
    contact3 = None

    #If more than one contact is associated with the alert set, the following variables are set to them
    if len(contacts) > 1:
        contact2 = int(contacts[1])
    if len(contacts) > 2:
        contact3 = int(contacts[2])

    note = "Alert " + name + " Updated To " + str(time.strftime("%I:%M %p"))
    if desc:
        note += "The user included the following message: " + desc
    dt_now = datetime.datetime.now()

    #The log note is saved to the database
    add_log_note(alert.user_id, dt_now, "Deleted Check-In", note, alert.message, alert.time)
    #The alert associated with the alert set is then updated and all of the changes are committed
    (db.session.query(Alert).filter_by(alert_id=alert_id)).update(
    {'message': desc, 'a_name': name, 'time': time, 'interval': interval, 'contact_id1': contact1, 'contact_id2': contact2, 'contact_id3': contact3})
    db.session.commit()

    #The user is then re-routed to the main besafe page
    return redirect("/bs_alerts")


@alerts_bp.route("/delete_alert/<alert_id>", methods=["POST"])
def delete_alert(alert_id):
    """Saves the edits to a recurring alert set"""
    #Relevant Alert is Queried
    alert = Alert.query.filter_by(alert_id=alert_id).one()

    #The variable "note" is set to what the log note will be
    note = "Alert " + alert.a_name + " Deleted"

    #The current datetime is queried
    dt_now = datetime.datetime.now()

    #The log note is saved to the database
    add_log_note(alert.user_id, dt_now, "Deleted Check-In", note, alert.message, alert.time)
    #The alert associated with the alert set is then deleted
    (db.session.query(Alert).filter_by(alert_id=alert_id)).delete()
    db.session.commit()

    #The user is then re-routed to the main besafe page
    return redirect("/bs_alerts")
