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

from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
#from dotenv import load_dotenv, find_dotenv

from auth import requires_auth

location_bp = Blueprint('location_bp', __name__)

@location_bp.route("/geo_point", methods=["POST"])
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
