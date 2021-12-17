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
from model import User, Contact, Alert, CheckIn, ReqCheck, connect_to_db, db, User_log
import requests
import logging
from Components.helpers import (check_in, create_alert, send_alert_contacts, send_alert_user, check_alerts, add_log_note)
from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from auth import requires_auth

logs_bp = Blueprint('logs_bp', __name__)

@logs_bp.route("/delete_log", methods=["GET"])
def delete_log():
    """Saves the edits to a recurring alert set"""
    user = User.query.filter_by(email=session['current_user']).one()
    #The alert associated with the alert set is then deleted
    to_delete = db.session.query(User_log).filter_by(user_id=user.user_id).all()
    for td in to_delete:
        db.session.delete(td)
    db.session.commit()
    url = "/edit_profile"
    print("Delete Log triggered")
    #The user is then re-routed to the main besafe page
    return redirect("/edit_profile")
