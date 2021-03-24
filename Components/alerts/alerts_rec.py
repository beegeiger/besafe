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

alerts_rec_bp = Blueprint('alerts_rec_bp', __name__)

############################################################3
"""Recurring AlertSets Paths"""

@alerts_rec_bp.route("/add_recset", methods=["POST"])
def add_rec_alertset():
    """Adds a recurring Alert-Set to the dBase"""
    user = User.query.filter_by(email=session['current_user']).one()
    alert_sets_all = AlertSet.query.filter_by(user_id=user.user_id).all()

    #Gets the alert and alert set info from the form on the add a new rec set page
    name = request.form['set_nam']
    desc = request.form['descri']
    interval = request.form['interval']
    contacts = request.form.getlist('contact')
    print("name1: ", name, type(name), len(name))

    if len(name)== 0:
        name = "Alert Set " + str(len(alert_sets_all))
    print("name2: ", name, type(name), len(name))
    #Queries the current user
    user = User.query.filter_by(email=session['current_user']).one()

    dt = datetime.datetime.now()
    #Creates a new alert set, adds it to the dBase, commits, and then queries the just-created alert set
    new_alert_set = AlertSet(user_id=user.user_id, start_datetime=dt, a_desc=desc, interval=interval, a_name=name)
    db.session.add(new_alert_set)
    db.session.commit()
    alert_set_q = AlertSet.query.order_by(AlertSet.start_datetime.asc()).first()
    alert_set_qall = AlertSet.query.order_by(AlertSet.start_datetime.desc()).all()
    
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
    new_alert = Alert(alert_set_id=alert_set_q.alert_set_id, user_id=user.user_id, contact_id1=contact1,
                      contact_id2=contact2, contact_id3=contact3, interval=interval, message=desc, time=datetime.datetime.now().time())
    print("From /add_recset: alert_set_q, new_alert, alert_set_qall", alert_set_q, new_alert, alert_set_qall)
    db.session.add(new_alert)
    db.session.commit()

    return redirect("/bs_alerts")


@alerts_rec_bp.route("/save_recset/<alert_set_id>", methods=["POST"])
def save_recset(alert_set_id):
    """Saves the edits to a recurring alert set"""

    #Gets the alert and alert set info from the form
    name = request.form['set_name']
    desc = request.form['descri']
    interval = request.form['interval']
    contacts = request.form.getlist('contact')

    #The Alert-Set is updated in the dBase with the new data
    (db.session.query(AlertSet).filter_by(alert_set_id=alert_set_id)).update(
    {'a_name': name, 'a_desc': desc, 'interval': interval})

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
    (db.session.query(Alert).filter_by(alert_set_id=alert_set_id)).update(
    {'message': desc, 'interval': interval, 'contact_id1': contact1, 'contact_id2': contact2, 'contact_id3': contact3})
    db.session.commit()

    #The user is then re-routed to the main besafe page
    return redirect("/bs_alerts")

###################################################################
"""Recurring Alerts Paths"""