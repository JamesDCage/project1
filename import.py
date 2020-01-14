# Create SQL tables for this project
# and import book data from CSV file

import csv    # Read & write comma-separated value files
import os     # Lets us read environment variables

# Connect to SQL database
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Link to existing postgresql database (stored in DATABASE_URL)
engine = create_engine(os.getenv("DATABASE_URL"))

# Create object to execute SQL commands
db = scoped_session(sessionmaker(bind=engine))


def main():

    # SQL commands to create tables
    create_books = """
        CREATE TABLE books
          (  book_id SERIAL PRIMARY KEY,
             isbn    VARCHAR(15),
             title   VARCHAR(63),
             author  VARCHAR(63),
             year    INT )  """

    create_users = """
        CREATE TABLE users
          (  user_id  SERIAL PRIMARY KEY,
             NAME     VARCHAR(127),
             username VARCHAR(63),
             pw_hash  VARCHAR(255) ) """

    create_reviews = """
        CREATE TABLE reviews
          (  review_id SERIAL PRIMARY KEY,
             book_id   INT REFERENCES books(book_id),
             user_id   INT REFERENCES users(user_id),
             rating    INT,
             body      TEXT )  """

    # Create tables
    db.execute(create_books)
    db.execute(create_users)
    db.execute(create_reviews)

    # Populate books table with data from CSV
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)  # Skip header line

    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})

    db.commit()  # None of the above SQL commands are sent to the db until this line


if __name__ == "__main__":
    main()