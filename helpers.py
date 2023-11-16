from flask import session, redirect
from functools import wraps
import dateutil.parser


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


def m_to_mi(value):
    return value / 1609


def human_readable_datetime(value):
    # format should be like "Nov 15, 2023 @ 10:20"
    return dateutil.parser.isoparse(value).strftime("%b %d, %Y @ %I:%M%p")