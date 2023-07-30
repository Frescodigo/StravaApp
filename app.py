import sqlite3
from flask import Flask, jsonify, render_template, redirect, request, session, url_for
from flask_session import Session
from helpers import calc_objective, login_required, m_to_ft, m_to_mi, start_of_week, s_to_min, update_goals
import requests

# Configure app
app = Flask(__name__)

# Configure db
# db = SQL("sqlite:///goals.db")
db_con = sqlite3.connect("goals.db")
db_cur = db_con.cursor()

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom Jinja variables
app.jinja_env.filters["m_to_ft"] = m_to_ft
app.jinja_env.filters["m_to_mi"] = m_to_mi
app.jinja_env.filters["s_to_min"] = s_to_min

# API variables
token_url = "https://www.strava.com/oauth/token"
CLIENT_ID = 100993
CLIENT_SECRET = "e79f1196ee2c0d7b0021b619a97dc3a94f1f5a3d"
APP_URL = "http://127.0.0.1:5000"

# App specific variables
CATEGORIES = ['distance', 'duration', 'elevation']
TIME_SPANS = ['daily-avg.', 'daily-min.', 'week']


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

    # Download Activities from Strava's API
    activities = get_activities()
    # Update the user's progress once goal and information data are defined
    goals = get_and_update_goals(activities)

    return render_template("index.html", activities=activities, athlete=session.get("user")["athlete"], goals=goals, categories=CATEGORIES, time_spans=TIME_SPANS)


# Log user in
@app.route("/login")
def login():
    session.clear()
    return render_template("login.html", app_url=APP_URL)

# Generate an access token
@app.route("/exchange_token")
def get_token():
    print('yippy')
    session["authorization-code"] = request.args.get("code")
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': session["authorization-code"],
        'grant_underscore': 'authorization_code'
    }
    session["user"] = requests.post(token_url, data=data).json()
    return redirect("/")


# Add goals to the database
@app.route("/addgoal", methods=["POST"])
@login_required
def add_goal():
    # Check that the user submitted a valid goal
    category = request.form.get("category")
    if category not in CATEGORIES:
        return redirect("/failure")
    objective = request.form.get("objective")
    try:
        objective = int(objective)
        if objective <= 0:
            raise ValueError
    except ValueError:
        return redirect("/failure")
    time_span = request.form.get("time-span")
    print(time_span)
    if not time_span or time_span not in TIME_SPANS:
        return redirect("/failure")
    objective_to_store = 7
    if time_span != 'daily-min':
        objective_to_store = calc_objective(objective, category)
    db_cur.execute("INSERT INTO goals(athlete_id, category, objective, time_span, start) \
        values(?, ?, ?, ?, ?)", session.get("user")["athlete"]["id"], category, objective_to_store, time_span, start_of_week())
    return redirect("/")


# Don't allow user to input goals that aren't accepted
@app.route("/failure")
def failure():
    return render_template("failure.html")


# Get user data?
@app.route("/user")
@login_required
def get_userdata():
    return jsonify(session["user"])


# Get user activities
@app.route("/activities")
@login_required
def get_activities():
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + session.get('user')['access_token']}
    params = {
        'after': start_of_week()
    }
    result = requests.get(activities_url, headers=header, params=params).json()
    return [i for i in result if i['type'] == 'Run']


# Get goals
@app.route("/goals")
@login_required
def get_and_update_goals(activities=None):
    res = db_cur.execute("SELECT * FROM goals WHERE athlete_id = ? AND start >= ?", session.get("user")["athlete"]["id"], start_of_week())
    goals = res.fetchall()
    if activities:
        goals = update_goals(db={'cur': db_cur, 'con': db_con}, goals=goals, activities=activities)
    return goals

