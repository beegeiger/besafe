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

from auth import requires_auth
from functools import wraps
from os import environ as env
from dotenv import load_dotenv, find_dotenv

from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode


contacts_bp = Blueprint('contacts_bp', __name__)

@contacts_bp.route("/contacts", methods=["POST"])
def add_contact():
    """Adds a user's new contact's info to the dBase"""

    #Creates variables from the form on the contacts page
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    #c_type = request.form['c_type']
    message = request.form['message']

    #Queries the current user
    user = User.query.filter_by(email=session['current_user']).one()

    #Creates the new Contact object, adds it to the dBase and commits the addition
    new_contact = Contact(user_id=user.user_id, name=name, email=email, phone=phone, c_message=message)
    db.session.add(new_contact)
    db.session.commit()

    return redirect("/contacts")

@contacts_bp.route("/del_contact/<contact_num>")
def delete_contact(contact_num):
    """Deletes a user's contact from the dBase"""

    #Queries the contact in question, deletes it from the dBase, and commits
    contact = Contact.query.filter_by(contact_id=contact_num).one()
    db.session.delete(contact)
    db.session.commit()

    return redirect("/contacts")


@contacts_bp.route("/edit_contact/<contact_num>", methods=["POST"])
def edit_contact(contact_num):
    """Edit's a contact's info"""

    #Creates variables from the form on the contacts page
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']

    #Queries the contact in question, edits it in the dBase, and commits
    contact = Contact.query.filter_by(contact_id=contact_num).one()
    ((db.session.query(Contact).filter_by(contact_id=contact_num)).update(
    {'name':name, 'email':email, 'phone':phone, 'c_message':message}))
    db.session.commit()

    return redirect("/contacts")