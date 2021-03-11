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

contacts_bp = Blueprint('contacts_bp', __name__)