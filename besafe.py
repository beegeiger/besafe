import flask
import bcrypt
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



################################################################

@app.route("/")
def go_home():
    """Renders the safework homepage. (Tested)"""
    return render_template("homepage.html")


@app.route("/register", methods=["GET"])
def register_form():
    """Goes to registration Form. (Tested)"""

    """Creating empty strings to send through jinja so that if someone is redirected
     from /register(POST), their data will still be in the registration form"""
    email_input = ""
    username = ""
    fname = ""
    lname = ""
    about_me = ""

    #Renders registration page with empty form variables
    return render_template("register.html", email=email_input, username=username,
                           fname=fname, lname=lname, about_me=about_me)


@app.route("/register", methods=["POST"])
def register_process():
    """Registration Form. (Tested)"""

    """Creating empty strings in case there aren't already
                data being passed from the registration redirect"""
    fname = ""
    lname = ""

    #Sets variables equal to the form values
    email_input = request.form['email_input']
    email2 = request.form['email_input2']
    phone = request.form['phone']

    pw_input = request.form['password']
    password2 = request.form['password2']

    username = request.form['username']
    tagline = request.form['tagline']
    location = request.form['location']
    p_word = bytes(pw_input, 'utf-8')
    hashed_word = bcrypt.hashpw(p_word, bcrypt.gensalt()).decode('utf-8')

    #These two categories need to be worked out better
    # user_type = request.form['user_type']
    # second_type = request.form['2nd']
    
    timezone = request.form['timezone']


    if pw_input != password2:
        flash("Your passwords don't match!")
        return render_template("register.html", email=email_input, username=username, fname=fname,
                               lname=lname, about_me=about_me)

    """Checks to make sure values exist in the optional fields
                before setting the variables equal to the form values"""
    if len(request.form['fname']) >= 1:
        fname = request.form['fname']
    if len(request.form['lname']) >= 1:
        lname = request.form['lname']


    #Checking that the e-mail address field at least includes a "." and a "@"
    if "." not in email_input or "@" not in email_input:
        flash(email_input + " is not a valid e-mail address!")
        return render_template("register.html", email=email_input, username=username,
                               fname=fname, lname=lname, about_me=about_me)

    #Checking that the e-mail address hasn't already been registered
    elif User.query.filter_by(email=email_input).all() != []:
        flash(email_input + """This e-mail has already been registered! Either sign in with it,
                use a different e-mail address, or reset your password if you forgot it.""")
        return render_template("register.html", email=email_input, username=username, fname=fname,
                               lname=lname, about_me=about_me)

    #Checking that the username is available
    elif User.query.filter_by(username=username).all() != []:
        flash(email_input + "This username is already in use! Please try another one!")
        return render_template("register.html", email=email_input, username=username, fname=fname,
                               lname=lname, about_me=about_me)

    #Checking that the password length is at least 6
    elif len(pw_input) < 6:

        flash("Your password must be at least 5 characters long! Try again.")
        return render_template("register.html", email=email_input, username=username, fname=fname,
                               lname=lname, about_me=about_me)

    #Otherwise, the new user's information is added to the database
    else:        
        new_user = User(email=email_input, password=hashed_word, username=username, fname=fname,
                        lname=lname, description=about_me, tagline=tagline, location=location,
                        email2=email2, phone=phone, timezone=timezone)
        db.session.add(new_user)
        db.session.commit()
    return redirect('/login')

@app.route("/login", methods=["GET"])
def log_in():
    """Render's the log-in page if user not in session,
     otherwise redirects to the homepage (Tested)"""

    if 'current_user' in list(session.keys()):
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    """Gets login info, verifies it, & either redirects to the forums or
    gives an error message (Tested)"""

    #Sets variable equal to the login form inputs
    email_input = request.form['email_input']
    pw_input = request.form['pw_input']
    user_query = User.query.filter(User.email == email_input).all()

    if user_query == []:
        flash('There is no record of your e-mail address! Please try again or Register.')
        print("No Record")
        return render_template("login.html")


    #Queries to see if the email and pword match the database. If so, redirects to the safewalk page.
    else:
        p_word = user_query[0].password
        if isinstance(pw_input, str):
            pw_input = bytes(pw_input, 'utf-8')
        passwd = bytes(p_word, 'utf-8')


        if bcrypt.hashpw(pw_input, passwd) == passwd:
            session['current_user'] = email_input
            flash('You were successfully logged in')
            return redirect("/sw_main")

        #Otherwise, it re-renders the page and throws an error message to the user
        else:
            flash('Your e-mail or password was incorrect! Please try again or Register.')
            return render_template("login.html")


@app.route("/logout")
def logout():
    """Logs user out and deletes them from the session (Tested)"""

    del session['current_user']

    flash('Bye! You have been succesfully logged out!')
    return redirect("/login")


@app.route("/profile")
def user_profile():
    """Renders user's profile"""

    user = User.query.filter_by(email=session['current_user']).one()

    return render_template("user_page.html", user=user, email=user.email, username=user.username,
                           fname=user.fname, lname=user.lname, about_me=user.description, tagline=user.tagline, location=user.location)



@app.route("/edit_profile", methods=["GET"])
def edit_page():
    """Renders the edit profile page"""

    user = User.query.filter_by(email=session['current_user']).one()

    return render_template("edit_profile.html", email=user.email, username=user.username,
                           fname=user.fname, lname=user.lname, about_me=user.description, user=user)



@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    """Submits the profile edits"""


    #Gets info from html form and dbase
    email_input = request.form['email_input']
    pw_input = request.form['password']
    username = request.form['username']
    fname = request.form['fname']
    tagline = request.form['tagline']
    location = request.form['location']
    lname = request.form['lname']
    about_me = request.form['about_me']
    email2 = request.form['email_input2']
    phone = request.form['phone']
    timezone = request.form['timezone']
    user = User.query.filter_by(email=session['current_user']).one()


    p_word = user.password
    if isinstance(pw_input, str):
        pw_input = bytes(pw_input, 'utf-8')
    passwd = bytes(p_word, 'utf-8')

    if bcrypt.hashpw(pw_input, passwd) == passwd:
        (db.session.query(User).filter(
            User.email == session['current_user']).update(
                {'fname': fname, 'lname': lname, 'email': email_input,
                 'username': username, 'description': about_me, 'email2': email2, 'phone': phone,
                 'timezone': timezone}))
        db.session.commit()
        flash('Your Profile was Updated!')
        return redirect("/profile")
        

    #Otherwise, it flashes a message and redirects to the login page
    else:
        flash('Your e-mail or password was incorrect! Please try again or Register.')
        return redirect("/edit_profile")

@app.route("/bs_alerts")
def besafe_alerts():
    """Renders the main safewalk page including a user's alert-sets"""

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
        print(a_set)
        aset_alerts = []
        a_set.total = 0

        #Loops through the alerts and adds the datetime for each to the aset_alerts list
        for alert in alerts:
            print(alert)
            if alert.active == True:
                print(alert)
            if a_set.alert_set_id == alert.alert_set_id and a_set.interval and alert.active == False:
                tim = now + datetime.timedelta(minutes=a_set.interval)
                aset_alerts.append(tim)
                print(tim)
            elif a_set.alert_set_id == alert.alert_set_id and a_set.interval and alert.active == True:
                aset_alerts.append(alert.datetime)
                print(alert.datetime)
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
                print('aset_alerts:')
                print(aset_alerts)
                aset_alerts.sort()
                print('aset_alerts0:')
                print(aset_alerts[0])
                print(now)
                a_set.next_alarm = aset_alerts[0]
                a_set.next_alarm_dis = aset_alerts[0].strftime("%I:%M %p, %m/%d/%Y")
                d1 = now - aset_alerts[0]
                print(d1)
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
                print(a_set.total)
            else:
                a_set.next_alarm_dis = now.strftime("%I:%M %p, %m/%d/%Y")

        #If there are no alerts, the current datetime is used as a placeholder
        else:a_set.next_alarm_dis = now.strftime("%I:%M %p, %m/%d/%Y")

    for a_s in alert_sets:
        if len(a_s.a_name) > 14:
            a_s.a_name = a_s.a_name[:9] + "..." + a_s.a_name[-4:]


    return render_template("besafe_alerts.html", alert_sets=alert_sets, timezone=user.timezone, user=user)

@app.route("/sw_getting_started")
def get_started():
    """Renders the 'Getting Started with SafeWalk' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    con_length = len(contacts)

    return render_template("getting_started_safewalk.html", contacts=contacts, con_length=con_length, timezone=user.timezone)

@app.route("/rec_alerts")
def recurring_alerts():
    """Renders the 'Create a Recurring Alert-Set' Page"""

    #Queries the current user and their contact info
    user = User.query.filter_by(email=session['current_user']).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    return render_template("recurring_alerts.html", contacts=contacts, timezone=user.timezone)

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

    #Gets the alert and alert set info from the form on the add a new rec set page
    name = request.form['set_name']
    desc = request.form['descri']
    interval = request.form['interval']
    contacts = request.form.getlist('contact')

    #Queries the current user
    user = User.query.filter_by(email=session['current_user']).one()

    #Creates a new alert set, adds it to the dBase, commits, and then queries the just-created alert set
    new_alert_set = AlertSet(user_id=user.user_id, a_name=name, a_desc=desc, interval=interval)
    db.session.add(new_alert_set)
    db.session.commit()
    alert_set = AlertSet.query.filter(AlertSet.user_id == user.user_id, AlertSet.a_name == name).first()

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
    new_alert = Alert(alert_set_id=alert_set.alert_set_id, user_id=user.user_id, contact_id1=contact1,
                      contact_id2=contact2, contact_id3=contact3, interval=interval, message=desc)
    db.session.add(new_alert)
    db.session.commit()

    return redirect("/sw_main")

@app.route("/edit_recset/<alert_set_id>")
def edit_recset_page(alert_set_id):
    """Renders the page to edit a recurring alert set"""

    #Queries the user, alert_set, user's contacts, and associated alerts
    user = User.query.filter_by(email=session['current_user']).one()
    alert_set = AlertSet.query.filter_by(alert_set_id=alert_set_id).one()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()
    alert = Alert.query.filter_by(alert_set_id=alert_set_id).one()

    return render_template("edit_recurring_alerts.html", alert_set=alert_set, contacts=contacts, alert=alert, timezone=user.timezone)

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

    #The user is then re-routed to the main safewalk page
    return redirect("/sw_main")

@app.route("/add_schedset", methods=["POST"])
def add_sched_alertset():
    """Adds a new scheduled alert set"""

    #Iniates date and end date variables and sets them to None
    date = None
    end_date = None

    #If the user enters a date or end_date, the variables are then updated to that value
    if len(request.form['date']) > 2:
        date = request.form['date']
    if len(request.form['end_date']) > 2:
        end_date = request.form['end_date']

    #Gets the alert set name, description, and then queries the current user
    name = request.form['set_name']
    desc = request.form['descri']
    user = User.query.filter_by(email=session['current_user']).one()

    #A new alert set object is then created, added to the dBase, and commited
    new_alert_set = AlertSet(user_id=user.user_id, a_name=name, a_desc=desc, date=date, end_date=end_date)
    db.session.add(new_alert_set)
    db.session.commit()

    #The just-created alert set is then queried to get the alert_set_id
    alert_set = AlertSet.query.filter(AlertSet.user_id == user.user_id, AlertSet.a_name == name).first()

    #The user is then redirected to the scheduled set edit page for this alert set
    return redirect("/edit_schedset/" + str(alert_set.alert_set_id))

@app.route("/edit_schedset/<alert_set_id>")
def edit_schedset_page(alert_set_id):
    """Renders the page where a scheduled alert set can be edited"""

    #The user, their alert_sets, alerts, and contacts are queried
    user = User.query.filter_by(email=session['current_user']).one()
    alert_set = AlertSet.query.filter_by(alert_set_id=alert_set_id).one()
    alerts = Alert.query.filter_by(alert_set_id=alert_set_id).order_by(asc(Alert.alert_id)).all()
    contacts = Contact.query.filter_by(user_id=user.user_id).order_by(asc(Contact.contact_id)).all()

    #This information is then sent to the rendered edit page
    return render_template("edit_sched_alerts.html", alert_set=alert_set, contacts=contacts, alerts=alerts, timezone=user.timezone)

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

    #Queries the current user
    user = User.query.filter_by(email=session['current_user']).one()
    
    #Gets the alert info from the form on the edit sched set page
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
    
    #Creates a new alert object, adds it to the dBase, commits, and redirects back to the edit page
    new_alert = Alert(alert_set_id=alert_set_id, user_id=user.user_id, contact_id1=contact1,
                      contact_id2=contact2, contact_id3=contact3, message=message, time=time)
    db.session.add(new_alert)
    db.session.commit()
    return redirect("/edit_schedset/" + str(alert_set_id))

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

#####################################################

if __name__ == "__main__":
    # start_runner()
    print("should be working")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    connect_to_db(app, 'postgresql:///besafe')
    print("Connected to DB.")
    app.run()
