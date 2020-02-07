# Used by Flask to generate pages and interact with databases

import os
from flask import Flask, flash, redirect, render_template, request, session, Markup
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, good_reads_info

from tempfile import mkdtemp  # DO I NEED THIS??

app = Flask(__name__)

# REMOVE FOLLOWING LINE BEFORE SUBMITTING
os.environ["DATABASE_URL"] = "postgres://sjxgnmkszhvvdc:d8add5033b1fec41278632fc2d7c50ddd0a28f07f066c9e3589cee6dbda7974c@ec2-174-129-33-181.compute-1.amazonaws.com:5432/d8oipsseui1nq1"


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


@app.route("/book/<string:book_id>", methods=["GET", "POST"])
@login_required
def book(book_id):
    # User reached route via POST (as by submitting a form via POST)
    # Note: as of Feb 6 20, no "else" statement. 
    if request.method == "POST":
        my_rating = request.form.get("my_rating")
        my_review = request.form.get("my_review")

        # Check to be sure the review is valid before inserting it into the database
        if my_rating or my_review:
            user_id = session["user_id"]
            db.execute("INSERT INTO reviews (book_id, user_id, rating, body) VALUES (:book_id, :user_id, :rating, :body)",
                        {"book_id": book_id, "user_id": user_id, "rating": my_rating, "body":my_review})
            db.commit()  # None of the above SQL commands are sent to the db until this line   
            # Thank the reader for the review
            flash("Thank you for your review!")

        else:
            # If no valid review was submitted, flash an error and continue building the page.
            flash("A review must contain a star rating, some text, or both.")


    # Gather data on this book for display on page
    find_books = f"""
        SELECT * 
        FROM books 
        WHERE book_id=:book_id limit 1"""    

    rows = db.execute(find_books, {"book_id": book_id}).fetchall()

    hits = len(rows)
    if hits:
        # If a book is found in the db, pack the data for display on page
        book_data = {
        "ISBN" : rows[0][1],
        "title" : rows[0][2],
        "author" : rows[0][3],
        "year" : rows[0][4]  }

        goodreads_data = good_reads_info(book_data["ISBN"])
        if goodreads_data:
            book_data["gr_reviews"] = goodreads_data['work_ratings_count']
            book_data["gr_rating"] = goodreads_data['average_rating']
        else:
            book_data["gr_reviews"] = None

    else:
        # No books found for some reason
        flash("OOPS! There's no record of that book in our database.")
        return render_template("index.html")        

    # Now get all reviews for this book

    book_query = """ SELECT users.name, 
                            users.user_id, 
                            reviews.rating, 
                            reviews.body 
                    FROM   reviews 
                            JOIN users 
                            ON reviews.user_id = users.user_id 
                    WHERE  book_id=:book_id"""

    rows = db.execute(book_query, {"book_id":book_id}).fetchall()

    # Add Finda Book review information to book_data
    book_data["fb_reviews"] = len(rows) if len(rows) else None
    num_ratings,sum_ratings = 0,0
    for review in rows:
        if review[2]:
            num_ratings += 1
            sum_ratings += review[2]
    book_data["fb_rating"] = None if not num_ratings else str(sum_ratings/num_ratings)[:4]


    # If the current user has reviewed this book, put that review in a list
    user_review = [review for review in rows if review[1] == session["user_id"]]

    # Put reviews by other users in a separate list
    other_reviews = [review for review in rows if not review[1] == session["user_id"]]

    # Display page
    return render_template("book.html", book_data=book_data, user_review=user_review, other_reviews=other_reviews)







@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        field_name = request.form.get("fieldname")
        search_text = request.form.get("searchtext")
        
        if not field_name:
            flash("Please enter a full or partial author name, book title, or ISBN.")
            return render_template("index.html")
        elif not search_text:
            flash("Please select the field to search ('Title', 'Author', or 'ISBN')")
            return render_template("index.html")


        # SQL command to find books

        max_books = 200 # Maximium number of results to return
        # Format search text for "like" search in SQL
        search_text = '%' + search_text + '%'

        find_books = f"""
            SELECT * 
            FROM books 
            WHERE UPPER({field_name}) LIKE UPPER(:searchtext) limit {max_books}"""

        rows = db.execute(find_books, {"searchtext": search_text}).fetchall()
        hits = len(rows)

        # Sort by field searched on. For example, in order by title if title search.
        def s_key(item):

            def clip_article(title):
                # Remove leading articles (a, an, the) from title if present
                # Only do this if there are 2 or more words in the title.
                chunks = title.split(' ', 1)
                if len(chunks)>1 and chunks[0].upper() in ['A','AN','THE']: 
                    return chunks[1].upper()
                return title.upper()

            field_name = request.form.get("fieldname")
            if field_name == "isbn":
                return item[1]
            elif field_name == "title":
                return clip_article(item[2])
            else:
                # Default to Author
                return item[3].upper()+clip_article(item[2])  # Sort by Author first, then by title.

        if len(rows):
            # Sort, using key defined above
            rows.sort(key=s_key)
            # Insert header, to be printed by jinja2 code on index.html
            rows.insert(0, ("ID","ISBN","Title","Author","Year"))
            
        flash(f"Search by {field_name} for {search_text[1:-1]}: {hits} books found.")
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
                session["user_id"] = rows[0][0]

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
                session["user_id"] = rows[0][0]

                # Redirect user to home page
                flash(f"Welcome {rows[0][1]}!")
                return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")