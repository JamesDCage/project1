
import os
from flask import Flask, flash, redirect, render_template, request, session, Markup, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, good_reads_info
import json

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# print(good_reads_info("1402792808"))



# json_query = """
#             SELECT title, 
#                    author, 
#                    year, 
#                    isbn 
#             FROM   books 
#             WHERE  isbn = '0670037729' 
# """

# json_dict ={columns[x]: db.execute(json_query).fetchall()[0][x] for x in range(4)}
# print(json_dict)
# book_raw = db.execute(json_query).fetchall()
# print(book_raw)

columns = ('title', 'author','year', 'isbn', 'average_score', 'review_count')

stats_query = f"""
              SELECT {','.join(columns[:4])},
                     Avg(rating)            AS average_score, 
                     Count(reviews.book_id) AS review_count 
              FROM   books 
                     FULL OUTER JOIN reviews 
                            ON books.book_id = reviews.book_id 
              WHERE  isbn=:isbn
              GROUP  BY reviews.book_id, 
                     {','.join(columns[:4])}"""


rows = db.execute(stats_query, {"isbn":'J0670037729'}).fetchall()
if len(rows):
    json_dict={columns[x]: rows[0][x] for x in range(len(columns))}
    json_dict["average_score"] = float(json_dict["average_score"])
else:
    json_dict='crap'

print(json_dict)
app = Flask(__name__)
with app.app_context():
    xxx = jsonify(json_dict)

print(xxx)

# json_dict["average_score"], json_dict["review_count"] = float(rows[0][0]), rows[0][1]

# app_json = json.dumps(json_dict)

# print(app_json)

# this_user = 2
# this_book = 4684

# rows = db.execute("SELECT * FROM reviews WHERE book_id =:book_id AND user_id=:user_id",
#                     {"book_id":this_book, "user_id":this_user}).fetchall()



# rows = db.execute("SELECT * FROM reviews WHERE book_id =:book_id AND NOT user_id=:user_id",
#                     {"book_id":this_book, "user_id":this_user}).fetchall()

# print(rows)

# book_query = """ SELECT users.name, 
#                         users.user_id, 
#                         reviews.rating, 
#                         reviews.body 
#                  FROM   reviews 
#                         JOIN users 
#                           ON reviews.user_id = users.user_id 
#                  WHERE  book_id=:book_id"""

# rows = db.execute(book_query, {"book_id":this_book}).fetchall()

# print(rows)

# print("me review", [review for review in rows if review[1] == this_user])

# print([review for review in rows if not review[1] == this_user])