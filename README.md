**BeSafe (CheckInWithMe) Safety System**\
#besafe #CheckInWithMe #SexWorker #Python #Flask

The BeSafe system is built to be hosted on the new CheckInWithMe website (yet to launch). The site will allow users to pre-set scheduled check-ins with the site. Then approaching the scheduled check-in time, a user can check in with the site using SMS, e-mail, or the application itself in a browser. If a user checks in at the appointed time, nothing happens. However, if the check-in is missed, a pre-set message wuth the user's location/activities will be sent to pre-set friends/family to warn them to try to get in contact with the user. In this initial version, check-ins made with the browser can also include single gps coordinates of the check-in location that will be added to the message. In future versions, including Android and iOS apps, more comprehensive (though optional) gps tracking will be included.

The basic BeSafe system is being built from the original Safework SafeWalk system designed to do the same thing, but focused specifically on Sex Workers. The CheckInWithMe BeSafe Project is meant to be more inclusive and to be a tool for every and anyone who is concerned about their safety and wants a (non-911) option to get help if something goes wrong.

The BeSafe System is built based on a basic Python3 Flask application and uses jquery and ajax to render site pages. It uses the Auth0 API to login via a new account with an e-mail, facebook login, and google login. In the past, thw Twilio API was used for SMS and the Mailgun API was used for email, but before the project is redeployed the cost and ease of use of API's will be re-evaluated.

The BeSafe project was developed using Ubuntu 18.1, but should be able to be run on anything 16.1 or higher.

### Prerequisites

-Running a Linux System (Developed and Tested on Ubuntu 18.04)

-System can be run on Python 3.6.5+

### Installing

-Clone/Download the repo from https://github.com/beegeiger/besafe

-Add "/env" directory to your working directory

-Create a virtual environment ($sudo python3 -m venv ./env) and activate it ($source env/bin/activate)

-Install requirements ($pip3 install -r requirements.txt)

-Create psql database called "besafe" ($createdb besafe)

-Seed Database: Run file model.py ($python3 model.py)

-Run besafe.py ($python3 besafe.py)

-The app should be running on your local system!

## Notes on Running

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
