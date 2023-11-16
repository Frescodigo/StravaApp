import sqlite3
from flask import Flask, jsonify, render_template, redirect, request, session, url_for
from flask_session import Session
from helpers import calc_objective, login_required, m_to_mi, human_readable_datetime
import os
import requests

# Configure app
app = Flask(__name__)
app.jinja_env.filters['m_to_mi'] = m_to_mi
app.jinja_env.filters['time'] = human_readable_datetime

# Configure db
db_con = sqlite3.connect("goals.db")
db_cur = db_con.cursor()

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure environment variables 
CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
if not CLIENT_ID:
    print("Environment variable 'STRAVA_CLIENT_ID' not set")
    quit()

CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
if not CLIENT_SECRET:
    print("Environment variable 'STRAVA_CLIENT_SECRET' not set")
    quit()

# API variables
token_url = "https://www.strava.com/oauth/token"
APP_URL = "http://127.0.0.1:5000"

# Show run activity/goals if logged in, send to login otherwise
@app.route("/")
def index():
    if not session.get("authorization-code"):
        return redirect("/login")

    # Refresh access token for API if need be
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': session.get("authorization-code"),
        'grant_type': 'refresh_token',
        'refresh_token': session.get('user')['refresh_token']
    }

    res = requests.post(token_url, data=data).json()
    session['user']['access_token'] = res['access_token']

    # Get Athlete info from Strava's API
    athlete = get_athlete()

    # Download Activities from Strava's API
    activities = get_activities()

    return render_template("index.html", athlete=athlete, activities=activities)


# Log user in
@app.route("/login")
def login():
    session.clear()
    return render_template("login.html", app_url=APP_URL)

# Generate an access token
@app.route("/exchange_token")
def get_token():
    session["authorization-code"] = request.args.get("code")
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': session["authorization-code"],
        'grant_underscore': 'authorization_code'
    }
    session["user"] = requests.post(token_url, data=data).json()
    return redirect("/")


# Get user activities
@app.route("/activities")
@login_required
def get_activities():
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + session.get('user')['access_token']}
    result = requests.get(activities_url, headers=header).json()

    return [i for i in result if i['type'] == 'Run']

# Get athlete data
@app.route("/athlete")
@login_required
def get_athlete():
    athlete_url = "https://www.strava.com/api/v3/athlete"
    header = {'Authorization': 'Bearer ' + session.get('user')['access_token']}
    result = requests.get(athlete_url, headers=header).json()
    return result