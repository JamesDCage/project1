
import os
from flask import Flask, flash, redirect, render_template, request, session, Markup
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, good_reads_info
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# print(good_reads_info("1402792808"))

this_user = 2
this_book = 4684

rows = db.execute("SELECT * FROM reviews WHERE book_id =:book_id AND user_id=:user_id",
                    {"book_id":this_book, "user_id":this_user}).fetchall()

if rows:
    print(rows)
else:
    print("Nothing here")

rows = db.execute("SELECT * FROM reviews WHERE book_id =:book_id AND NOT user_id=:user_id",
                    {"book_id":this_book, "user_id":this_user}).fetchall()

print(rows)

book_query = """ SELECT users.name, 
                        users.user_id, 
                        reviews.rating, 
                        reviews.body 
                 FROM   reviews 
                        JOIN users 
                          ON reviews.user_id = users.user_id 
                 WHERE  book_id=:book_id"""

rows = db.execute(book_query, {"book_id":this_book}).fetchall()

print(rows)

print("me review", [review for review in rows if review[1] == this_user])

print([review for review in rows if not review[1] == this_user])