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

app = Flask(__name__)
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
################################################################

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

######################################################################3

# @app.route("/api_key", methods=["POST"])
# def api_key():
#     return google_maps_key

@app.route("/")
def go_home():
    """Renders the besafe homepage. (Tested)"""
    return render_template("homepage.html")

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
    session['current_user'] = userinfo['email']
    user = User.query.filter_by(email=userinfo['email']).all()
    if user == []:
        new_user = User(name=userinfo['name'], email=userinfo['email'], username=userinfo['nickname'], fname=userinfo['given_name'], lname=userinfo['family_name'], created_at=datetime.datetime.now())
        db.session.add(new_user)
        db.session.commit()
        return redirect('/edit_profile')
    db.session.commit()
    return redirect('/edit_profile')

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))


@app.route("/login", methods=["GET"])
def log_in():
    """Render's the log-in page if user not in session,
     otherwise redirects to the homepage (Tested)"""
    print('login visited')
    # if 'current_user' in list(session.keys()):
    #     return redirect("/")
    # else:
    # return render_template("login.html")
    uri = "https://besafe.ngrok.io/callback"
    print(type(uri))
    return auth0.authorize_redirect(redirect_uri=uri, audience='https://dev-54k5g1jc.auth0.com/api/v2/')


@app.route("/logout")
def logout():
    """Logs user out and deletes them from the session (Tested)"""
    # del session['current_user']
    # flash('Bye! You have been succesfully logged out!')
    # return redirect("/login")
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('go_home', _external=True), 'client_id': '78rUTjeVusqU3vYXyvNpOQiF8jEacf55'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route("/profile")
def user_profile():
    """Renders user's profile"""

    user = User.query.filter_by(email=session['current_user']).one()

    return render_template("user_page.html", user=user, email=user.email, username=user.username,
                           fname=user.fname, lname=user.lname, about_me=user.description, tagline=user.tagline, location=user.location)



@app.route("/edit_profile", methods=["GET"])
@requires_auth
def edit_page():
    """Renders the edit profile page"""

    user = User.query.filter_by(email=session['current_user']).one()

    return render_template("edit_profile.html", user=user)



@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    """Submits the profile edits"""

    print("form: ", request.form)
    #Gets info from html form and dbase
    email_input = request.form['email_input']
    fname = request.form['fname']
    lname = request.form['lname']
    phone = request.form['phone']
    timezone = request.form['tzim']
    user = User.query.filter_by(email=session['current_user']).one()

    (db.session.query(User).filter(
        User.email == session['current_user']).update(
            {'fname': fname, 'lname': lname, 'email': email_input,
                'phone': phone,'timezone': timezone}))
    db.session.commit()
    flash('Your Profile was Updated!')
    return redirect("/")




@app.route("/bs_alerts")
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

    alert_sets = AlertSet.query.filter_by(user_id=user.user_id).all()
    al_sets = []
    alerts = Alert.query.filter_by(user_id=user.user_id).all()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    con_length = len(contacts)

    #If the user has added no contacts, they are re-routed to the 'getting started' page
    if con_length < 1:
        return redirect("/sw_getting_started")

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
                # days = math.floor(d2 / 86400)
                # hours = math.floor((d2 - (days * 86400)) / 3600)
                # minutes = math.floor((d2 - (days * 86400) - (hours * 3600)) / 60)
                # seconds = math.floor(d2 - (days * 86400) - (hours * 3600) - (minutes * 60))
                # print(minutes)
                # a_set.countdown = datetime.time(int(hours), int(minutes), int(seconds))
                # a_set.days = int(days)
                # a_set.hours = int(hours)
                # a_set.minutes = int(minutes)
                # a_set.seconds = int(seconds)
                a_set.total =int(d2)
                # if d1 < datetime.timedelta(seconds=0):
                #     a_set.total = 0

            else:
                a_set.next_alarm_dis = now.strftime("%I:%M %p, %m/%d/%Y")

        #If there are no alerts, the current datetime is used as a placeholder
        else:a_set.next_alarm_dis = now.strftime("%I:%M %p, %m/%d/%Y")

    for a_s in alert_sets:
        if len(a_s.a_name) > 14:
            a_s.a_name = a_s.a_name[:9] + "..." + a_s.a_name[-4:]


    return render_template("besafe_alerts.html", alert_sets=alert_sets, alerts=alerts, timezone=user.timezone, user=user, contacts=contacts)

@app.route("/sw_getting_started")
def get_started():
    """Renders the 'Getting Started with besafe' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    con_length = len(contacts)

    return render_template("getting_started_besafe.html", contacts=contacts, con_length=con_length, timezone=user.timezone)



@app.route("/sched_alerts")
def scheduled_alerts():
    """Renders the 'Create a Scheduled Alert-Set' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    return render_template("scheduled_alerts.html", contacts=contacts, timezone=user.timezone)


@app.route("/contacts")
def user_contacts():
    """Renders the User's 'contacts' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    return render_template("contacts.html", contacts=contacts, timezone=user.timezone)


@app.route("/contacts", methods=["POST"])
def add_contact():
    """Adds a user's new contact's info to the dBase"""

    #Creates variables from the form on the contacts page
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    c_type = request.form['c_type']
    message = request.form['message']

    #Queries the current user
    user = User.query.filter_by(email=session['current_user']).one()

    #Creates the new Contact object, adds it to the dBase and commits the addition
    new_contact = Contact(user_id=user.user_id, name=name, email=email, phone=phone, c_type=c_type, c_message=message)
    db.session.add(new_contact)
    db.session.commit()

    return redirect("/contacts")


@app.route("/del_contact/<contact_num>")
def delete_contact(contact_num):
    """Deletes a user's contact from the dBase"""

    #Queries the contact in question, deletes it from the dBase, and commits
    contact = Contact.query.filter_by(contact_id=contact_num).one()
    db.session.delete(contact)
    db.session.commit()

    return redirect("/contacts")


@app.route("/edit_contact/<contact_num>", methods=["POST"])
def edit_contact(contact_num):
    """Edit's a contact's info"""

    #Creates variables from the form on the contacts page
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    c_type = request.form['c_type']
    message = request.form['message']

    #Queries the contact in question, edits it in the dBase, and commits
    contact = Contact.query.filter_by(contact_id=contact_num).one()
    ((db.session.query(Contact).filter_by(contact_id=contact_num)).update(
    {'name':name, 'email':email, 'phone':phone, 'c_type':c_type, 'c_message':message}))
    db.session.commit()

    return redirect("/contacts")


@app.route("/add_recset", methods=["POST"])
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
    alert_set_q = AlertSet.query.order_by(AlertSet.start_datetime.desc()).first()

   

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
                      contact_id2=contact2, contact_id3=contact3, interval=interval, message=desc)
    db.session.add(new_alert)
    db.session.commit()

    return redirect("/bs_alerts")

@app.route("/save_recset/<alert_set_id>", methods=["POST"])
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
    return redirect("/sw_main")

@app.route("/add_schedset", methods=["POST"])
def add_sched_alertset():
    """Adds a new scheduled alert set"""
    print("Add Schedset Submitted")
    #Iniates date and end date variables and sets them to None
    # date = None
    # end_date = None

    #If the user enters a date or end_date, the variables are then updated to that value
    # if len(request.form['date']) > 2:
    #     date = request.form['date']
    # if len(request.form['end_date']) > 2:
    #     end_date = request.form['end_date']
    user = User.query.filter_by(email=session['current_user']).one()
    alert_sets_all = AlertSet.query.filter_by(user_id=user.user_id).all()
 
    print("Form: ", request.form)
    #Gets the alert set name, description, and then queries the current user
    name = request.form['set_nam']
    print("name: ", name)
    desc = request.form['descri']
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
    return str(alert_set.alert_set_id)


@app.route("/edit_set/<alert_set_id>", methods=["POST"])
def save_schedset(alert_set_id):
    """Saves the scheduled alert set beind edited"""

    #Gets the alert set details from the form
    date = request.form['date']
    end_date = request.form['end_date']
    name = request.form['set_name']
    desc = request.form['descri']

    #Queries the dBase for the alert set, updates it, commits, and redirects the user back to edit page
    (db.session.query(AlertSet).filter_by(alert_set_id=alert_set_id)).update(
    {'date': date, 'end_date': end_date, 'a_name': name, 'a_desc': desc})
    db.session.commit()
    return redirect("/edit_schedset/" + str(alert_set_id))

@app.route("/edit_al/<alert_id>", methods=["POST"])
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

@app.route("/add_alert/<alert_set_id>", methods=["POST"])
def add_sched_alert(alert_set_id):
    """Saves a new scheduled alert"""
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
    db.session.add(new_alert)
    db.session.commit()
    return "Alert Added"

@app.route("/activate/<alert_set_id>")
def activate_alertset(alert_set_id):
    """Activates an alert set"""

    #The alert set in question is queried
    alert_set = AlertSet.query.filter_by(alert_set_id=alert_set_id).one()
    
    #Variables set to the current date, time, and datetime are created for convenience
    time = datetime.datetime.now().time()
    date = (datetime.datetime.today())
    dt = datetime.datetime.now()
    
    #An empty list is created to store the datetimes of the alerts associated with the alert set
    dt_list = []
    
    #If there is no start date, the start date is set to today
    if alert_set.date == None:
        db.session.query(AlertSet).filter_by(alert_set_id=alert_set_id).update({'date': date, 'start_datetime': dt})
    
    #If the alert set is scheduled (not recurring), the alert times are added to the the dt_list
    if alert_set.interval == None:
        alerts = Alert.query.filter_by(alert_set_id=alert_set_id).all()
        for alert in alerts:
            db.session.query(Alert).filter_by(alert_id=alert.alert_id).update({'active': True, 'start_time': time})
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
        alert = Alert.query.filter_by(alert_set_id=alert_set_id).one()
        db.session.query(Alert).filter_by(alert_id=alert.alert_id).update({'active': True, 'start_time': time, 'time': dtime_int.time(), 'datetime': dtime_int})
        dt_list.append(dtime_int)
    
    #The alert set is updated to be active and its commited
    db.session.query(AlertSet).filter_by(alert_set_id=alert_set_id).update({'active': True, 'start_time': time, 'start_datetime': dt})
    db.session.commit()
    
    #The alert datetime list is sorted and the earliest time is then sent back to the page
    dt_list.sort()
    alarm_dt = dt_list[0].strftime("%I:%M %p, %m/%d/%Y")
    return str(alarm_dt)

@app.route("/deactivate/<alert_set_id>")
def deactivate_alertset(alert_set_id):
    """Deactivates an alert set"""

    #The alert set is queried and updated
    (db.session.query(AlertSet).filter_by(alert_set_id=alert_set_id)).update(
    {'active': False})
    
    #All alerts associated with the alert set are queried and updated, and it's all commited
    alerts = Alert.query.filter_by(alert_set_id=alert_set_id).all()
    for alert in alerts:
        if alert.interval:
            db.session.query(Alert).filter_by(alert_id=alert.alert_id).update(
            {'active': False, 'checked_in': False, 'time': None, 'datetime': None})
        else:
            db.session.query(Alert).filter_by(alert_id=alert.alert_id).update(
            {'active': False, 'checked_in': False,'datetime': None})
    db.session.commit()
    return "Alert Set Deactivated"

@app.route("/check_ins")
def checkin_page():
    """Renders the User's check-in page"""

    #The current user and check-ins are queried and the page is rendered
    user = User.query.filter_by(email=session['current_user']).one()
    check_ins = CheckIn.query.filter_by(user_id=user.user_id).all()
    return render_template("checkins_page.html", check_ins=check_ins, timezone=user.timezone)

@app.route("/add_check_in", methods=["POST"])
def add_new_checkin():
    """Using POST, a new check-in is added from the check-in page"""

    #Get's the check-in details from the form on the page and runs the check_in helper-function
    text = request.form['check_text']
    user = User.query.filter_by(email=session['current_user']).one()
    
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
        message = "Your Check-In has been received! Your next alarm is due in " + str(minutes) + " minutes, so you must check in between " + str(check_time) + " and " + str(time) + "."
    
    #Otherwise a message is created explaining that there are no active alerts
    else:
        message = "Your check-in has been received! You don't have any alerts currently active."
    
    #The message is then sent back to the user as confirmation
    if len(all_alerts) > 0:
        send_alert_user(all_alerts[0].alert_id, message)

    return redirect("/check_ins")

@app.route("/feedback", methods=["POST"])
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

@app.route("/user_code", methods=["POST"])
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
@app.route("/incoming_mail", methods=["POST"])
def mailin():
    """Route where incoming mail is sent from mailgun"""

    #Access some of the email parsed values:
    sender = request.form['From']
    send_address = request.form['sender']
    subject = request.form['subject']
    text = request.form['body-plain']
    body = str(text)

    #The user is queried using the e-mail address
    user = User.query.filter_by(email=str.strip(send_address)).all()
    if user == []:
        user = User.query.filter_by(email2=str.strip(send_address)).all()

    if user != []:
        print("User Found by email address")

    while user == []:
        left = body.find("(")
        if left == -1:
            break
        else:
            right = body.find(")")
            if right == left + 5:
                user = User.query.filter_by(user_code=body[(left + 1):(left + 5)]).all()
                body = body[0:left] + body[(left + 1):]
                body = body[0:right] + body[(right + 1):]
                if user != []:
                    print("User Found by user code")
    
    if user == []:
        print("No User Was Found")
    else:
        send_email(send_address, "Thank You! Your Check-In has been received and logged!")

    #Assuming a user is found, the check-in helper-function is run
    if len(user) >= 1:
        u_id = user[0].user_id
        check_in(u_id, text)
    print(send_address)
    print("Email Message Received")
    return "Email Message Received"

@app.route('/incoming_sms', methods=['POST'])
def smsin():
    """Route where incoming SMS messages are sent from Bandwidth"""
    
    number = request.form['From']
    message_body = request.form['Body']
    body = str(message_body)

    # # Access some of the SMS parsed values:
    # dat = request.data
    # data = json.loads(dat.decode(encoding="utf-8", errors="strict"))
    # message_body = data['text']
    # phone = data['from']

    if len(number) > 10:
        number = number[-10:]

    print("Number =" + str(number))
    print("Body =" + body)


    #The user is queried using the phone-number

    user = User.query.filter_by(phone=str(number)).all()

    if user != []:
        print("User Found by phone number")

    while user == []:
        left = body.find("(")
        if left == -1:
            break
        else:
            right = body.find(")")
            if right == left + 5:
                user = User.query.filter_by(user_code=body[(left + 1):(left + 5)]).all()
                body = body[0:left] + body[(left + 1):]
                body = body[0:right] + body[(right + 1):]
                if user != []:
                    print("User Found by user code")
    
    if user == []:
        print("No User Was Found")
    else:
        send_message(number, "Thank You " + user[0].fname + "! Your Check-In has been received and logged!")
    
    #Assuming a user is found, the check-in helper-function is run
    if len(user) >= 1:
        u_id = user[0].user_id
        check_in(u_id, message_body)
    print(number)
    print(user)
    print("SMS Received")
    return "SMS Received"



@app.route("/geo_point", methods=["POST"])
def add_geo_point():
    """Adds New Geo Point for user's phone"""
    user = User.query.filter_by(email=session['current_user']).one()
    now = datetime.datetime.now()
    lat = str(request.form['lat'])
    lon = str(request.form['long'])
    print("Lat + Long =")
    print(lat, lon)
    geo = GeoPoint(user_id=user.user_id, latitude=lat, longitude=lon, datetime=now)
    db.session.add(geo)
    db.session.commit()
    return "success"


#####################################################

if __name__ == "__main__":
    # start_runner()
    print("should be working")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # connect_to_db(app, 'postgresql:///besafe')
    print("Connected to DB.")
    Debug(app)
    app.run(debug=True)
    app.run()
