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

# TODO: Get a real host address
APP_IP = os.environ.get("STRAVA_APP_IP") # Debug only, I think
if not APP_IP:
    print("Environment variable 'STRAVA_APP_IP' not set")
    quit()

# API variables
token_url = "https://www.strava.com/oauth/token"
APP_URL = "http://" + APP_IP + ":5000"

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
    name = session['user']['athlete'].get('firstname', 'Champion')

    return render_template("index.html", name=name, app_url=APP_URL)


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

    after_timestamp = request.args.get('cutoff', 0)

    print(after_timestamp)

    activities = []
    request_page_num = 1
    per_page = 200
    while True:
        params = {'per_page': per_page, 'page': request_page_num, 'after': after_timestamp}
        activity_request = requests.get(activities_url, headers=header, params=params).json()
        
        if activities:
            activities.extend(activity_request)
        else:
            activities = activity_request

        if len(activity_request) < per_page:
            break

        request_page_num += 1
    
    activities = [activity for activity in activities if activity['type'] == 'Run']
    return activities


# Get athlete data
@app.route("/athlete")
@login_required
def get_athlete():
    athlete_url = "https://www.strava.com/api/v3/athlete"
    header = {'Authorization': 'Bearer ' + session.get('user')['access_token']}
    result = requests.get(athlete_url, headers=header)
    print("*****************", result)
    result = result.json()
    print("#############:", result)
    return result


if __name__ == '__main__':
    app.run(host=APP_IP, debug=True)  
