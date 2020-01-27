# Used by Flask to generate pages and interact with databases

import os
from flask import Flask, flash, redirect, render_template, request, session, Markup
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

from tempfile import mkdtemp  # DO I NEED THIS??

app = Flask(__name__)
#
# REMOVE FOLLOWING LINE BEFORE SUBMITTING
# os.environ["DATABASE_URL"] = "postgres://sjxgnmkszhvvdc:d8add5033b1fec41278632fc2d7c50ddd0a28f07f066c9e3589cee6dbda7974c@ec2-174-129-33-181.compute-1.amazonaws.com:5432/d8oipsseui1nq1"
#

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("searchtext"):
            flash("Please enter a full or partial author name, book title, or ISBN.")
            return render_template("index.html")
        elif not request.form.get("fieldname"):
            flash("Please select the field to search ('Title', 'Author', or 'ISBN')")
            return render_template("index.html")


        # SQL command to find books

        max_books = 100 # Maximium number of results to return
        search_text = '%' + request.form.get("searchtext") + '%'


        find_books = f"""
            SELECT * 
            FROM books 
            WHERE UPPER({request.form.get("fieldname")}) LIKE UPPER(:searchtext) limit {max_books}"""

        rows = db.execute(find_books, {"searchtext": search_text}).fetchall()

# Sort results - do this after successful print
# Sort by field you searched?

# print results

# Don't print ID
# Add link to book page - do this last?


        # If any results returned, sort and add header info
        # Sort results

        field_name = request.form.get("fieldname")

        def s_key(item):
            global field_name
            if field_name == "ISBN":
                return item[1]
            elif field_name == "Title":
                return item[2]
            else:
                # Default to Author
                return item[3]






        if len(rows):
            rows.sort(key=s_key)
            rows.insert(0, ("ID","ISBN","Title","Author","Year"))
            
            

        flash(f"{len(rows)} books found.")
        return render_template("index.html", matrix=rows)




    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not (request.form.get("username") and request.form.get("password")):
            flash("Please enter your user name and password.")
            return render_template("login.html")

        else:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              {"username": request.form.get("username")}).fetchall()

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0][3], request.form.get("password")):
                flash(Markup('Username or password not found. Please <a href="/register" class="alert-link">register</a> or try again.'))
                return render_template("login.html")

            else:
                # Remember which user has logged in
                session["user_id"] = rows[0][2]

                # Redirect user to home page
                flash(f"Welcome {rows[0][1]}!")
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure all fields are submitted
        if not (request.form.get("name") and request.form.get("username") and
                request.form.get("password") and request.form.get("confirmation")):
            flash("All fields are required to register.")
            return render_template("register.html")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords must match. Please try again.")
            return render_template("register.html")

        else:

            # Be sure the user name is not duplicated. First, query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              {"username": request.form.get("username")}).fetchall()

            # Then, ensure no user by this name in database
            if len(rows) != 0:
                flash("This user name is already taken. Please try again.")
                return render_template("register.html")

            else:

                # Now insert user into database
                pw_hash = generate_password_hash(request.form.get("password"))
                new_user = request.form.get("username")
                name = request.form.get("name")

                db.execute("INSERT INTO users (name, username, pw_hash) VALUES (:name, :username, :pw_hash)",
                           {"name": name, "username": new_user, "pw_hash": pw_hash})

                db.commit()  # None of the above SQL commands are sent to the db until this line

                # Now assign user to session - that is, log user in
                # Query for user to obtain id
                rows = db.execute("SELECT * FROM users WHERE username = :username",
                                  {"username": request.form.get("username")}).fetchall()

                # Remember which user has logged in
                session["user_id"] = rows[0][2]

                # Redirect user to home page
                flash(f"Welcome {rows[0][1]}!")
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")