from besafe import app
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
from auth import requires_auth

@app.route("/")
def go_home():
    """Renders the besafe homepage. (Tested)"""
    return render_template("homepage.html")

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

@app.route("/edit_profile", methods=["GET"])
@requires_auth
def edit_page():
    """Renders the Profile page"""

    #Queries User
    user = User.query.filter_by(email=session['current_user']).one()

    #Returns the Profile Template
    return render_template("edit_profile.html", user=user)    