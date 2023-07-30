from calendar import timegm
from datetime import date, timedelta
from flask import session, redirect
from functools import wraps
from time import gmtime, strftime, timezone


def calc_progress(goal):
    if goal['time_span'] == 'daily-avg.':
        return goal['progress'] / 7
    return goal['progress']


def calc_objective(objective, category):
    if category == 'distance':
        return objective * 1609
    elif category == 'duration':
        return objective * 60
    else:
        return objective / 3.28084



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("authorization-code") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def m_to_ft(value):
    return value * 3.28084


def m_to_mi(value):
    return value / 1609


def start_of_week():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return int(timegm(monday.timetuple()) + timezone)


def s_to_min(value):
    return str(timedelta(seconds=value))


def update_goals(db, goals, activities):
    activity_keys = {
        'distance': 'distance',
        'duration': 'moving_time',
        'elevation': 'total_elevation_gain'
    }
    for goal in goals:
        goal_progress = 0
        category = goal['category']
        if goal['time_span'] == 'daily-min.':
            for day in range(7):
                date = strftime("%Y-%m-%d", gmtime(start_of_week() + day * 86400))
                date_activities = ([activity for activity in activities if activity['start_date_local'].startswith(date)])
                total_date_progress = 0
                for date_activity in date_activities:
                    total_date_progress += date_activity[activity_keys[category]]
                if total_date_progress > goal['objective']:
                    goal_progress += 1
        else:
            for activity in activities:
                goal_progress += activity[activity_keys[category]]
        if goal['progress'] != goal_progress:
            db[cur].execute("UPDATE goals SET progress = ? WHERE id = ?", goal_progress, goal['id'])
            db[con].commit()
            goal['progress'] = goal_progress
    return goals
