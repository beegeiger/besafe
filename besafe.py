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


#####################################################

if __name__ == "__main__":
    # start_runner()
    print("should be working")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    connect_to_db(app, 'postgresql:///besafe')
    print("Connected to DB.")
    app.run()
