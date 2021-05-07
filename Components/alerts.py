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
        db.session.query(Alert).filter_by(alert_id=alert_id).update({'date': date, 'start_datetime': dt})
    
    #If the alert set is scheduled (not recurring), the alert times are added to the the dt_list
    if alert.interval == None:
        db.session.query(Alert).filter_by(alert_id=alert_id).update({'active': True, 'start_time': time})
        if alert.date == None:
            dtime = datetime.datetime.combine(date, alert.time)
            db.session.query(Alert).filter_by(alert_id=alert.alert_id).update({'date': date, 'datetime': dtime})
            dt_list.append(dtime)
        else:
            dtime = datetime.datetime.combine(alert.date, alert.time)
            db.session.query(Alert).filter_by(alert_id=alert.alert_id).update({'datetime': dtime})
            dt_list.append(dtime)
    
    #If the alert set is recurring, the alert time is set to now + the time interval
    else:
        print("Interval = " + str(alert_set.interval))
        print("Rec Activated")
        # dtime = datetime.datetime.combine(date, time)
        # dt_list.append(dtime)
        dtime_int = dt + datetime.timedelta(minutes=alert_set.interval)
        db.session.query(Alert).filter_by(alert_id=alert.alert_id).update({'active': True, 'start_time': time, 'time': dtime_int.time(), 'datetime': dtime_int})
        dt_list.append(dtime_int)
    
    #Session is Commited
    db.session.commit()
    
    #The alert datetime list is sorted and the earliest time is then sent back to the page
    dt_list.sort()
    alarm_dt = dt_list[0].strftime("%I:%M %p, %m/%d/%Y")
    return alert

@alerts_bp.route("/deactivate/<alert_id>")
def deactivate_alertset(alert_id):
    """Deactivates an alert set"""

    #All alerts associated with the alert set are queried and updated, and it's all commited
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    if alert.interval:
        db.session.query(Alert).filter_by(alert_id=alert.alert_id).update(
        {'active': False, 'checked_in': False, 'time': None, 'datetime': None})
    else:
        db.session.query(Alert).filter_by(alert_id=alert.alert_id).update(
        {'active': False, 'checked_in': False,'datetime': None})
    db.session.commit()
    return "Alert Set Deactivated"

@alerts_bp.route("/add_alert", methods=["POST"])
def add_alert():
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

    if time == "":
        time = None
    if interval == "":
        interval = None

    if len(name)== 0:
        name = "Alert " + str(len(alerts_all))
    print("name2: ", name, type(name), len(name))
    #Queries the current user

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
                      contact_id2=contact2, contact_id3=contact3, interval=interval, message=desc, time=time)

    db.session.add(new_alert)
    db.session.commit()

    return redirect("/bs_alerts")


@alerts_bp.route("/save_alert/<alert_id>", methods=["POST"])
def save_recset(alert_id):
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

    #Initiates 3 contact variables, sets the first to the first contact and the next two to None
    contact1 = int(contacts[0])
    contact2 = None
    contact3 = None

    #If more than one contact is associated with the alert set, the following variables are set to them
    if len(contacts) > 1:
        contact2 = int(contacts[1])
    if len(contacts) > 2:
        contact3 = int(contacts[2])

    #The alert associated with the alert set is then updated and all of the changes are committed
    (db.session.query(Alert).filter_by(alert_id=alert_id)).update(
    {'message': desc, 'a_name': name, 'time': time, 'interval': interval, 'contact_id1': contact1, 'contact_id2': contact2, 'contact_id3': contact3})
    db.session.commit()

    #The user is then re-routed to the main besafe page
    return redirect("/bs_alerts")