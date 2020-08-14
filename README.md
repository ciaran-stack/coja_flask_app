# coja_flask_app
Coja is a web application that simplifies queries to the SEC database. Future applications on Coja will include NLP and data analysis

This repository contains the local version of the coja flask application. 

### Tech Stack
* **SQLAlchemy ORM** to be our ORM library of choice
* **PostgreSQL** as our database of choice
* **Python3** and **Flask** as our server language and server framework
* **Flask-Migrate** for creating and running schema migrations
* **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend

### Development Setup

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.

  ```
  $ cd ~
  $ pip3 install Flask
  ```

Second, [psql-ORM]
  ```
  $ cd ~
  $ apt-get install postgresql
  $ pip3 install flask-sqlaclhemy
  ```
  
  
### Run local app command
Make sure you are in the directory where the app is contained
  ```
  $ FLASK_APP=app.py flask run
  ```
  
### Setup Local DB
  ```
  $ createdb coja
  ```
  
### Run migrations to local DB from flask app
  ```
  $ flask db init
  $ flask db migrate
  $ flask db upgrade
  ```
