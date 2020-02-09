# Project 1

Web Programming with Python and JavaScript

James Cage JamesDCage@Gmail.com

## Background

This project follows CS50w  requirements with following stretch goals:
* Search results are sorted by search field. For example, if searching on isbn, sort by isbn.
* When sorted on title or author+title, articles (a, an, the) are removed with custom code.
* Code for home page is decorated to require log-in before using.
* If user attempts to access home page without first logging in, user is redirected to login page. As part of this action, a message appear with a link to the registration page.
* User table in database stores password hash, not raw password.


## Files

### Root

.gitignore: Defines files that are not included in git repository.

application.py: Python file, interacts with SQL database and jinja 2 template files.

books.csv: (Provided by CS50W) List of books for website

helpers.py: Python file containing misc. functions

import.py: Python file used to create SQL tables and import books.csv into the SQL database

project1.scss, project1.css: SASS file, compiled to CSS

README.md: This file

requirements.txt: Provided by CS50W, with some additions


### Templates

layout.html: Common html elements for all pages on this site using jinja 2.

index.html: Home page. Allows users to search and displays results of search, with links to individual books.  

book.html: Displays information about an individual book from this site and Goodreads. Allows user to review book.

login.html: Allows user to log into site.

register.html: Allows user to register for the site.