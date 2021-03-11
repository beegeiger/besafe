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
from dotenv import load_dotenv, find_dotenv

from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
from alerts.alert_sets import alert_set_bp
from alerts.alerts_rec import alerts_rec_bp
from alerts.alerts_sched import alerts_sched_bp

def check_in(user_id, notes):
    """Helper-function used to log a new check-in from any source"""

    #Date, time, and datetime objects are initiated for convenience
    time = datetime.datetime.now().time()
    date = (datetime.datetime.today())
    datetim = datetime.datetime.now()

    #A new check-in object is created, added, and commited
    new_check = CheckIn(user_id=user_id, notes=notes, time=time, date=date, datetime=datetim)
    db.session.add(new_check)
    db.session.commit()
    
    #All active alerts for the user are queried
    alerts = Alert.query.filter(Alert.user_id == user_id, Alert.active == True).all()
    
    #The alerts are looped through and all alerts within an hour are marked as checked-in
    for alert in alerts:
        if alert.datetime - datetim < datetime.timedelta(hours=1.5):
            if alert.interval:
                print("Alert:")
                print(alert)
                (db.session.query(Alert).filter_by(alert_id=alert.alert_id)).update(
                {'datetime': (alert.datetime + datetime.timedelta(minutes=alert.interval)), 'checked_in': True})
                db.session.query(AlertSet).filter_by(alert_set_id=alert.alert_set_id).update({'checked_in': True})
            else:
                (db.session.query(Alert).filter_by(alert_id=alert.alert_id)).update(
                {'datetime': (alert.datetime + datetime.timedelta(days=1)), 'checked_in': True})
                db.session.query(AlertSet).filter_by(alert_set_id=alert.alert_set_id).update({'checked_in': True})
    db.session.commit()
    return "Check In has been Logged!"

def create_alert(alert_id):
    """Helper Function for creating an alert's actual message body"""

    #Datetime object for now created for convenience
    datetim = datetime.datetime.now()

    #The alert in question, the user, the alert set, all other associated alerts, and the recent check-ins are all queried
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    user = User.query.filter_by(user_id=alert.user_id).one()
    alert_set = AlertSet.query.filter_by(alert_set_id=alert.alert_set_id).one()
    all_alerts = Alert.query.filter(alert.alert_set_id == alert.alert_set_id, alert.datetime > alert_set.start_datetime).all()
    check_ins = CheckIn.query.filter(checkin.user_id == user.user_id, abs(checkin.datetime - datetim) <  datetime.timedelta(days=1)).all()
    
    #An empty dictionary is created to store the associated events for the alert
    events = {}
    
    #A new string that will begin the alert message is created
    message_body = """This is a Safety Alert sent by {} {} through the SafeWork Project SafeWalk Alert system,
            found at safeworkproject.org \n \n""".format(user.fname, user.lname)
    
    #If there are notes on the alert set, they are added to the message
    if alert_set.notes:
        message_body += """The user has included the following messages when they made this alert and checked in \n \n {}""".format(alert_set.message)
    
    #For all associated alerts, if there is a message longer than 2 characters, the alert is added to the events dictionary
    for a_a in all_alerts:
        if len(a_a.message) > 2:
            events[a_a.datetime] = a_a
    
    #All check-ins are added to the events dictionary
    for chks in check_ins:
        events[chks.datetime] = chks

    #Loops through all of the ordered events in the dictionary
    for key in sorted(events.keys()):
        #If the event was a scheduled alarm
        if type(events[key]) == model.Alarm:
            #Different messages are added depending on whether the alarm was check-in for and if it had a message
            if events[key].checked_in == True:
                message_body += "An alarm was scheduled for {} which {} checked-in for.".format(key, user.fname)
                if events[key].message:
                    message_body += "The Alarm included the following notes: {} \n \n".format(events[key].message)
                else:
                    message_body += "\n \n"
            else:
                message_body += "An alarm was scheduled for {} which {} MISSED the checked-in for.".format(key, user.fname)
                if events[key].message:
                    message_body += "The Alarm included the following notes: {} \n \n".format(events[key].message)
                else:
                    message_body += "\n \n"
        #If it isn't an alarm, it's a check-in object which is then added to the main message body
        else:
            message_body += "{} checked in with the app at {} and included the following message: {}".format(user.fname, key, events[key].notes)
    
    #Different messages are added depending on how many contacts are sent the alert
    if alert.contact_id3:
        message_body += """Two other contacts have been sent this alert. If you know who it might be,
                        consider reaching out and co-ordinating your effort to help {}.""".format(user.fname)
    elif alert.contact_id2:
        message_body += """One other contact has been sent this alert. If you know who it might be,
                        consider reaching out and co-ordinating your effort to help {}.""".format(user.fname)
    else:
        message_body += """You were the only person sent this alert, so if anything can be done
                        to help {}, it is up to you! Good luck!!!""".format(user.fname)
    
    #The complete message body is then returned
    return message_body


def send_alert_contacts(alert_id, message_body):
    """Helper Function that actually sends the alerts over e-mail and sms"""
    
    #The current alert and user is queried
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    user = User.query.filter_by(user_id=alert.user_id).one()
    

    #An empty list is created and then filled with the contact objects associated with the alert
    contacts = []
    contacts += Contact.query.filter_by(contact_id=alert.contact_id1)
    if alert.contact_id2:
        contacts += Contact.query.filter_by(contact_id=alert.contact_id2)
    if alert.contact_id2:
        contacts += Contact.query.filter_by(contact_id=alert.contact_id3)
    
    #For each contact, an optional personal message is added to the message_body and is sent to email and sms
    for con in contacts:
        if con.c_message:
            body = con.c_message + message_body
        if con.email:
            send_email(con.email, body)
        if con.phone:
            send_sms(con.phone, body)
    return "Message Sent"

def send_alert_user(alert_id, message_body):
    """Helper Function that actually sends the alerts over e-mail and sms"""
    
    #The current alert and user is queried
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    user = User.query.filter_by(user_id=alert.user_id).one()
    
    if user.email2:
        send_email(user.email2, message_body)
        print('Sending to email2')
    elif user.email:
        send_email(user.email, message_body)
        print('Sending to email1')
    if user.phone:
        send_message(user.phone, message_body)
        print('Sending to phone')
    return "Messages Sent"

def check_alerts():
    """A Helper function to run every minute to check if any alerts need to be sent"""
    
    print("Checking For Alerts and Reminders Now")

    #Datetime object for now created for convenience
    datetim = datetime.datetime.now()
    yester = datetim - datetime.timedelta(days=1)

    with app.app_context():
        #All currently-active alerts are queried 
        alerts = Alert.query.filter_by(active=True).all()
        print(alerts)
        #If at least one alert is active, the alerts are looped through to see if any need to be sent
        if len(alerts) > 0:
            for alert in alerts:
                #A new variable 'difference' is set to the timedelt between the alert and the current time
                difference = alert.datetime - datetime.datetime.now()
                
                #All recent check-ins are queried and a new counter variable checks is set to 0
                check_ins = CheckIn.query.filter(CheckIn.user_id == alert.user_id, CheckIn.datetime  >=  yester).all()
                checks = 0
                
                #For each check-in, if it is within 90 minutes before the current time, the checks counter is added by 1
                for ch in check_ins:
                    dif = datetime.datetime.now() - alert.datetime
                    if dif <= datetime.timedelta(hours=1.5) and difference > datetime.timedelta(seconds=0):
                        checks += 1
                
                #If there is no check-in and the alert is within a minute, an alert is sent
                if abs(difference) <= datetime.timedelta(minutes=1) and abs(difference) > datetime.timedelta(seconds=0) and checks == 0 and alert.sent == False:
                    print('A CHECK-IN WAS MISSED AND AN ALERT IS BEING SENT NOW!')
                    message_body = create_alert(alert.alert_id)
                    send_alert_contacts(alert.alert_id, message_body)
                    #The alert object is updates to be marked sent and inactive and its commited
                    (db.session.query(Alert).filter_by(alert_id=alert.alert_id)).update({'sent': True, 'active': False})
                    (db.session.query(AlertSet).filter_by(alert_set_id=alert.alert_set_id)).update({'active': False})
                    db.session.commit()
                
                elif abs(difference) <= datetime.timedelta(minutes=1) and abs(difference) > datetime.timedelta(seconds=0) and checks < 0 and alert.sent == False:
                    db.session.query(AlertSet).filter_by(alert_set_id=alert.alert_set_id).update({'checked_in': False})


                #If there is no check in and it is 15 minutes before an alert, a reminder message is sent
                elif abs(difference) <= datetime.timedelta(minutes=15) and abs(difference) > datetime.timedelta(minutes=14) and checks == 0 and alert.sent == False:
                    print('A CHECK-IN REMINDER IS BEING SENT NOW!')
                    message_body = """Reminder! You have a Check-In Scheduled in 15 minutes. If you don't check-in
                    by responding to this text, emailing 'safe@safeworkproject.org', or checking in on the site at
                    'www.safeworkproject.org/check_ins', your pre-set alerts will be sent to your contact(s)!"""
                    send_alert_user(alert.alert_id, message_body)
    return