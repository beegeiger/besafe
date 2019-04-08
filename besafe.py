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



#####################################################

if __name__ == "__main__":
    # start_runner()
    print("should be working")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    connect_to_db(app, 'postgresql:///besafe')
    print("Connected to DB.")
    app.run()
