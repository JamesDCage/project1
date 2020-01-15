import requests
import urllib.parse

from flask import redirect, render_template, request, session, flash, Markup
from functools import wraps


# FOLLOWING FUNCTION SHOULD BE 100% REPLACED BY BOOTSTRAP FLASH MESSAGES
# def apology(message, code=400):
#     """Render message as an apology to user."""
#     def escape(s):
#         """
#         Escape special characters.

#         https://github.com/jacebrowning/memegen#special-characters
#         """
#         for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
#                          ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
#             s = s.replace(old, new)
#         return s
#     return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash(Markup('You must register to use this site. Please <a href="/register" class="alert-link">register</a> or log in.'))
            # return redirect("/login")
            return render_template("login.html")
        return f(*args, **kwargs)
    return decorated_function

# ADD CODE TO GET INFO FROM GOODREADS