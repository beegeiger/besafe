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

alerts_sched_bp = Blueprint('alerts_sched_bp', __name__)

############################################################3
"""Scheduled AlertSets Paths"""

@alerts_sched_bp.route("/add_schedset", methods=["POST"])
def add_sched_alertset():
    """Adds a new scheduled alert set"""
    print("Add Schedset Submitted")

    user = User.query.filter_by(email=session['current_user']).one()
    alert_sets_all = AlertSet.query.filter_by(user_id=user.user_id).all()
 
    print("Form: ", request.form)
    #Gets the alert set name, description, and then queries the current user
    name = request.form['set_nam']
    print("name: ", name)
    desc = request.form['descri']
    time = request.form['time']
    contacts = request.form.getlist('contact')
    print("descri: ", desc)
    
    if len(name)== 0:
        name = "Alert Set " + str(len(alert_sets_all))
    print("name2: ", name, type(name), len(name))
    #A new alert set object is then created, added to the dBase, and commited
    new_alert_set = AlertSet(user_id=user.user_id, a_name=name, a_desc=desc)
    db.session.add(new_alert_set)
    db.session.commit()

    #The just-created alert set is then queried to get the alert_set_id
    alert_set = AlertSet.query.filter(AlertSet.user_id == user.user_id, AlertSet.a_name == name).first()
    print("Type Alert Set :", type(alert_set))
    #The user is then redirected to the scheduled set edit page for this alert set
    print("Got Through Add SchedSet, Here's the alert set: ", alert_set)

    #Initiates 3 contact variables, sets the first to the first contact and the next two to None
    contact1 = int(contacts[0])
    contact2 = None
    contact3 = None

    #If more than one contact is associated with the alert set, the following variables are set to them
    if len(contacts) > 1:
        contact2 = int(contacts[1])
    if len(contacts) > 2:
        contact3 = int(contacts[2])


    new_alert = Alert(alert_set_id=alert_set.alert_set_id, user_id=user.user_id, contact_id1=contact1,
                      contact_id2=contact2, contact_id3=contact3, message=desc, time=time)
    
    db.session.add(new_alert)
    db.session.commit()

    return redirect("/edit_schedset/" + str(alert_set.alert_set_id))


@alerts_sched_bp.route("/edit_set/<alert_set_id>", methods=["POST"])
def save_schedset(alert_set_id):
    """Saves the scheduled alert set beind edited"""

    #Gets the alert set details from the form
    # date = request.form['date']
    # end_date = request.form['end_date']
    date = None
    end_date = None
    name = request.form['set_name']
    desc = request.form['descri']

    #Queries the dBase for the alert set, updates it, commits, and redirects the user back to edit page
    (db.session.query(AlertSet).filter_by(alert_set_id=alert_set_id)).update(
    {'date': date, 'end_date': end_date, 'a_name': name, 'a_desc': desc})
    db.session.commit()
    return redirect("/edit_schedset/" + str(alert_set_id))

@alerts_sched_bp.route("/edit_al/<alert_id>", methods=["POST"])
def edit_schedal(alert_id):
    """Saves the existing scheduled alert being edited"""

    #Queries alert in question current user
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    user = User.query.filter_by(email=session['current_user']).one()

    #Gets the alert information from the form on the page
    time = request.form['time']
    contacts = request.form.getlist('contact')
    message = request.form['check_mess']

    #Initiates 3 contact variables, sets the first to the first contact and the next two to None
    contact1 = int(contacts[0])
    contact2 = None
    contact3 = None

    #If more than one contact is associated with the alert set, the following variables are set to them
    if len(contacts) > 1:
        contact2 = int(contacts[1])
    if len(contacts) > 2:
        contact3 = int(contacts[2])

    #Queries and updates the alert, commits, and redirects back to the edit page
    (db.session.query(Alert).filter_by(alert_id=alert_id)).update(
    {'time': time, 'contact_id1': contact1, 'contact_id2': contact2, 'contact_id3': contact3, 'message': message})
    db.session.commit()
    return redirect("/edit_schedset/" + str(alert.alert_set_id))

###################################################################
"""Scheduled Alerts Paths"""

@alerts_sched_bp.route("/add_alert/<alert_set_id>", methods=["POST"])
def add_sched_alert(alert_set_id):
    """Saves a new scheduled alert"""
    user = User.query.filter_by(email=session['current_user']).one()
    alert_set = AlertSet.query.filter(AlertSet.user_id == user.user_id, AlertSet.alert_set_id == alert_set_id).first()
    #Queries the current user
    user = User.query.filter_by(email=session['current_user']).one()
    
    #Gets the alert info from the form on the edit sched set page
    time = request.form['time']

    
    #Initiates 3 contact variables, sets the first to the first contact and the next two to None
    contact1 = alert_set.contact_id1
    contact2 = alert_set.contact_id2
    contact3 = alert_set.contact_id3
    
    #If more than one contact is associated with the alert set, the following variables are set to them

    #Creates a new alert object, adds it to the dBase, commits, and redirects back to the edit page
    new_alert = Alert(alert_set_id=alert_set_id, user_id=user.user_id, contact_id1=contact1,
                      contact_id2=contact2, contact_id3=contact3, time=time)
    print("New Alert Just added: ", new_alert)
    db.session.add(new_alert)
    db.session.commit()
    return redirect("/edit_schedset/" + str(alert_set.alert_set_id))