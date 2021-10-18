## BeSafe (CheckInWithMe) Safety System
#besafe #CheckInWithMe #SexWorker #Python #Flask

The BeSafe system is built to be hosted on the new CheckInWithMe website (yet to launch). The site will allow users to pre-set scheduled check-ins with the site. Then approaching the scheduled check-in time, a user can check in with the site using SMS, e-mail, or the application itself in a browser. If a user checks in at the appointed time, nothing happens. However, if the check-in is missed, a pre-set message with the user's location/activities will be sent to pre-set friends/family to warn them to try to get in contact with the user. In this initial version, check-ins made with the browser can also include single gps coordinates of the check-in location that will be added to the message. In future versions, including Android and iOS apps, more comprehensive (though optional) gps tracking will be included.

The basic BeSafe system is being built from the original Safework SafeWalk system designed to do the same thing, but focused specifically on Sex Workers. The CheckInWithMe BeSafe Project is meant to be more inclusive and to be a tool for every and anyone who is concerned about their safety and wants a (non-911) option to get help if something goes wrong.

The BeSafe System is built based on a basic Python3 Flask application and uses jquery and ajax to render site pages. It uses the Auth0 API to login via a new account with an e-mail, facebook login, and google login. In the past, the Twilio API was used for SMS and the Mailgun API was used for email, but before the project is redeployed the cost and ease of use of API's will be re-evaluated.

### Prerequisites

-Running a Linux System (Developed and Tested on Ubuntu 18.04)

-System can be run on Python 3.6.5+

## Installing and Running

-Clone/Download the repo from https://github.com/beegeiger/besafe

-Add "/env" directory to your working directory

-Create a virtual environment ($sudo python3 -m venv ./env) and activate it ($source env/bin/activate)

-Install requirements ($pip3 install -r requirements.txt)

-Create psql database called "besafe" ($createdb besafe)

-Seed Database: Run file model.py ($python3 model.py)

-Run besafe.py ($python3 besafe.py)

-The app should be running on your local system!

### Notes on Running and Logging In

-The application uses the Auth0 API to login. For development, you can either set up secure login, or you can use the development backdoor (recommended). Instructions for both options are directly below.

-To get a full login-experience (optional), you need to acquire an Auth0 API key (as well as a facebook and/or google API key). Once you have that, Auth0 will only accept requests from an https uri. If you already have a uri with a TLS cert you can use for testing, add that uri to the Auth0 settings along with the application endpoint(s). Alternatively, using ngrok (or a comparable service), you can run your server through an ngrok proxy to give it an https uri. Make sure that you access the server through the ngrok url and not directly through localhost or Auth0 will not recognize it as a secure uri. Unfortunately, the free ngrok account doesn't give you a permanent uri, so if you use a free account, you will need to update the Auth0 endpoints every time you run the ngrok proxy so it matches the new origin. For that reason, a paid ngrok account is recommended for anyone interested in using this method in the long run.

-The alternative login flow for development (recommended) requires no additional API keys or accounts. Simply run the server using the steps described above in the beginning of the "Installing and Running" section. Then, once the homepage is rendered in your browser through localhost, simply visit [your localhost address and port]/login/development and you will be logged in using an account that bypasses Auth0 directly and logs you in as a dummy developer user (with no password or security) that has two dummy contacts associated with it (created in model.py). This should allow you to test most/all aspects of the application without messing with any external API's. You can modify this login method by changing the dummy account and contacts in the model.py file and/or editing the /login path found in besafe.py.

### Built With

* [Flask](http://flask.pocoo.org/) - The web framework used

