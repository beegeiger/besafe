"""Models and database functions for BeSafe App"""
from flask import jsonify, Flask
import datetime
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_debugtoolbar import DebugToolbarExtension

# from server import app

# Required to use Flask sessions and the debug toolbar
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///besafe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.app = app
#######################


class User(db.Model):
	"""User Table in SafeWork App"""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	username = db.Column(db.String(64), nullable=True)
	name = db.Column(db.String(64), nullable=True)
	fname = db.Column(db.String(64), nullable=True)
	lname = db.Column(db.String(64), nullable=True)
	email = db.Column(db.String(256))
	created_at = db.Column(db.DateTime, nullable=True)
	timezone = db.Column(db.String(48))
	phone = db.Column(db.String(28), nullable=True)


	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<user_id={} username={} name={} fname={} lname={} email={} created_at={} timezone={} phone={}>".format(
			self.user_id, self.username, self.name, self.fname, self.lname, self.email, self.created_at, self.timezone, self.phone)



 
class Contact(db.Model):
	"""SafeWalk Contacts"""

	__tablename__ = "contacts"

	contact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	name = db.Column(db.String(96))
	email = db.Column(db.String(200), nullable=True)
	phone = db.Column(db.String(48), nullable=True)
	c_type = db.Column(db.String(48), nullable=True)
	c_message = db.Column(db.String(1028), nullable=True)

	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<contact_id={} user_id={} name={} email={} phone={} c_type={} c_message={}>".format(
			self.contact_id, self.user_id, self.name, self.email, self.phone, self.c_type, self.c_message)

class AlertSet(db.Model):
	"""SafeWalk AlertSet"""

	__tablename__ = "alertsets"

	alert_set_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	a_name = db.Column(db.String(96))
	a_desc = db.Column(db.String(200), nullable=True)
	start_time = db.Column(db.Time, nullable=True)
	start_datetime = db.Column(db.DateTime, nullable=True)
	date = db.Column(db.Date, nullable=True)
	end_date = db.Column(db.Date, nullable=True)
	notes = db.Column(db.String(2056), nullable=True)
	interval = db.Column(db.Integer, nullable=True)
	active = db.Column(db.Boolean, default=False)
	checked_in = db.Column(db.Boolean, default=False)

	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<alert_set_id={} user_id={} a_name={} a_desc={} start_time={} start_datetime={} date={} end_date={} notes={} active={} checked_in={}>".format(
			self.alert_set_id, self.user_id, self.a_name, self.a_desc, self.start_time, self.start_datetime, self.date, self.end_date, self.notes, self.active, self.checked_in)

class Alert(db.Model):
	"""SafeWalk AlertSet"""

	__tablename__ = "alerts"

	alert_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	alert_set_id = db.Column(db.Integer, db.ForeignKey('alertsets.alert_set_id'))
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	contact_id1 = db.Column(db.Integer, db.ForeignKey('contacts.contact_id'))
	contact_id2 = db.Column(db.Integer, db.ForeignKey('contacts.contact_id'), nullable=True)
	contact_id3 = db.Column(db.Integer, db.ForeignKey('contacts.contact_id'), nullable=True)
	active = db.Column(db.Boolean, default=False)
	sent = db.Column(db.Boolean, default=False)
	time = db.Column(db.Time, nullable=True)
	date = db.Column(db.Date, nullable=True)
	interval = db.Column(db.Integer, nullable=True)
	start_time = db.Column(db.Time, nullable=True)
	message = db.Column(db.String(1028), nullable=True)
	datetime = db.Column(db.DateTime, nullable=True)
	checked_in = db.Column(db.Boolean, default=False)

	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<alert_id={} alert_set_id={} user_id={} contact_id1={} contact_id2={} contact_id3={} active={} sent={} time={} date={} start_time={} message={} datetime={} checked_in={}>".format(
			self.alert_id, self.alert_set_id, self.user_id, self.contact_id1, self.contact_id2, self.contact_id3, self.active, self.sent, self.time, self.date, self.start_time, self.message, self.datetime, self.checked_in)

class CheckIn(db.Model):
	"""SafeWalk Check-Ins"""

	__tablename__ = "checkins"

	check_in_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	notes = db.Column(db.String(2056), nullable=True)
	address = db.Column(db.String(512), nullable=True)
	time = db.Column(db.Time, nullable=True)
	date = db.Column(db.Date, nullable=True)
	datetime = db.Column(db.DateTime, nullable=True)
	lat = db.Column(db.String(256), nullable=True)
	lon = db.Column(db.String(256), nullable=True)

	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<check_in_id={} user_id={} notes={} address={} time={} date={} datetime={} lat={} lon={}>".format(
			self.check_in_id, self.user_id, self.notes, self.address, self.time, self.date, self.datetime, self.lat, self.lon)

class ReqCheck(db.Model):
	"""Required SafeWalk Check-Ins"""

	__tablename__ = "reqchecks"

	req_check_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	check_in_id = db.Column(db.Integer, db.ForeignKey('checkins.check_in_id'), nullable=True)
	alert_id = db.Column(db.Integer, db.ForeignKey('alerts.alert_id'))
	alert_set_id = db.Column(db.Integer, db.ForeignKey('alertsets.alert_set_id'))
	time = db.Column(db.Time, nullable=True)
	date = db.Column(db.Date, nullable=True)
	checked = db.Column(db.Boolean, nullable=True)


	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<req_check_id={} user_id={} check_in_id={} alert_id={} alert_set_id={} time={} date={} checked={}>".format(
			self.req_check_id, self.user_id, self.check_in_id, self.alert_id, self.alert_set_id, self.time, self.date, self.checked)

class Feedback(db.Model):
	"""Error Feedback from Users"""

	__tablename__ = "feedback"

	feedback_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	datetime = db.Column(db.DateTime, nullable=True)
	content = db.Column(db.String(2056))


	def __repr__(self):
		"""Provide helpful representation when printed."""
		return "<feedback_id={} user_id={} datetime={} content={}>".format(
			self.feedback_id, self.user_id, self.datetime, self.content)
 


################################################################################

def example_data():
	"""Example data to be used for testing."""
	#Deleting tables in case this file has been run before
	User.query.delete()
	Flag.query.delete()

	
	#Example Users
	u1 = User(password=bcrypt.hashpw("12356".encode(), bcrypt.gensalt()), username="LaceyKittey", fname="Lacey", lname="Kittey", email="lkitty@.com", created_at=datetime.now(), edited_at=datetime.now())
	u2 = User(password=bcrypt.hashpw("abcdef".encode(), bcrypt.gensalt()), username="HappyDoc", fname="Happy", lname="Doc", email="HDoc@.com", created_at=datetime.now(), edited_at=datetime.now())
	u3 = User(password=bcrypt.hashpw("Testing".encode(), bcrypt.gensalt()), username="Testing", fname="Dev", lname="Tester", email="Testing@gmail.com", created_at=datetime.now(), edited_at=datetime.now())
	


	db.session.add_all([u1, u2, u3])
	db.session.commit()



##############################################################################
# Helper functions

def connect_to_db(app, db_uri='postgresql:///besafe'):
	"""Connect the database to our Flask app."""
	# Configure to use our PstgreSQL database
	print("Connecting")
	# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	# db.app = app
	db.init_app(app)

if __name__ == "__main__":	
	connect_to_db(app, 'postgresql:///besafe')
	print("Connected to DB.")