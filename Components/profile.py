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
from model import User, Contact, Alert, CheckIn, ReqCheck, connect_to_db, db
import requests
import logging

from auth import requires_auth
from functools import wraps
from os import environ as env
from dotenv import load_dotenv, find_dotenv

from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode


profile_bp = Blueprint('profile_bp', __name__)





@profile_bp.route("/edit_profile", methods=["POST"])
def edit_profile():
    """Submits the profile edits"""


    #Gets info from html form and dbase
    email_input = request.form['email_input']
    fname = request.form['fname']
    lname = request.form['lname']
    phone = request.form['phone']
    timezone = request.form['tzim']

    #Queries User
    user = User.query.filter_by(email=session['current_user']).one()

    #Updates User Object in DB and Commits
    (db.session.query(User).filter(
        User.email == session['current_user']).update(
            {'fname': fname, 'lname': lname, 'email': email_input,
                'phone': phone,'timezone': timezone}))
    db.session.commit()
    
    flash('Your Profile was Updated!')
    
    #Refreshes the Profile Page
    return redirect("/edit_profile")

@profile_bp.route("/feedback", methods=["POST"])
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

@profile_bp.route("/user_code", methods=["POST"])
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