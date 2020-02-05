import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session, flash, Markup
from functools import wraps


def good_reads_info(isbn):
    """
    For a book (represented by its ISBN), extract review info from Goodreads.com
    """
    # This is the personal key of James Cage
    my_key = "xHCRAkFbkWQAsRuaraWYsg"

    # Request info from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": my_key, "isbns": isbn})

    # If found return info. If not, return None.
    try:
        # Return the portion of the response that contains a dictionary of books-specific information
        return res.json()["books"][0]
    except:
        return None


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash(Markup('You must register to use this site. Please <a href="/register" class="alert-link">register</a> or log in.'))
            return render_template("login.html")
        return f(*args, **kwargs)
    return decorated_function

