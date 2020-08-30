from flask import Flask, render_template, Response, flash, redirect, url_for, abort, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Resource, Api
from wtforms import Form, StringField, SelectField
import sys
from forms import TickerSearchForm
import random, string, httplib2
from flask_requests import request

# Authorization imports
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random, string
import json

app = Flask(__name__)

# configure DB by putting user name and local DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://joeyp@localhost:5432/coja'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ciaranmahon@localhost:5432/coja'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Enables migrations of DB changes
migrate = Migrate(app, db)

# Client access variable (read client_secrets.json)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Company(db.Model):
    """Represents a public company with a ticker and CIK from the SEC.gov site"""
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String)
    name = db.Column(db.String)
    cik_number = db.Column(db.String)

    def __repr__(self):
        """String object of Model attributes"""
        return f'id: {self.id} ticker: {self.ticker} name: {self.name} cik_num: {self.cik_number}'

    def details(self):
        """Dictionary of each attribute to reference in SQLAlchemy ORM queries"""
        return{
            'id': self.id,
            'ticker': self.ticker,
            'name': self.name,
            'cik_number': self.cik_number,
            }

    def short(self):
        """Used for SEARCH and returning only a company's name & ID"""
        return{
            'id': self.id,
            'ticker': self.ticker,
        }


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
@app.route('/login')
def showLogin():
    """Login page path"""
    # Create a unique, 32-character session token, each being random and generated by python libraries
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))

    # show login page
    return render_template('pages/login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameters'), 401)
        response.headers['Content-Type'] = 'applications/json'
        return response
    code = request.data
    try:
        oauth_fow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_fow.redirect_uri = 'postmessage'
        # exchange the auth code into a credentials object
        credentials = oauth_fow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps ('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check validity of token
    access_token = credentials.access_token
    # Google server verifies the token is good for usage
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

# If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dump(result.get('error')), 50)
        response.headers['Content-Type'] = 'applications/json'
    return response

    # verify that the access token is used for the int ended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'applications/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's"), 401)
        response.headers['Content-Type'] = 'applications/json'
        return response

    # check to see if the user is already logged in
    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'applications/json'
        return response

    # store the access token in the session for later use
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # get user information
    user_info_url = 'https://wwww.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = request.get(user_info_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: ' \
              '150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# DISCONNECT - Revoke a current user's token and reset their session
@app.route('/gdisconnect')
def gdisconnect():
    """Function logs a user out of Google Auth0 system """

    # Only disconnect a connected user.
    credentials = session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'applications/json'
        return response
    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')['0']

    if result['status'] == '200':
        # Reset user login
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']

        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'applications/json'
        return response


@app.route('/')
def home():
    """Display homepage of coja.io when application is opened"""
    return render_template('pages/home.html')


@app.route('/search_ticker', methods=['POST'])
def search():
    """Form on homepage to get passed parameter of ticker"""

    # get object from form
    ticker_object = request.form.get('search_ticker')

    # query database to get a ticker that matches the search term
    company_query = Company.query.filter(Company.ticker.ilike('%' + ticker_object + '%'))
    # create a list to iterate over on the results page
    company_list = list(map(Company.details, company_query))

    # dictionary object to render results on HTML page
    response = {
        'count': len(company_list),
        'data': company_list
    }

    return render_template('pages/search_company.html', results=response, search_term=ticker_object)


@app.route('/search_company_name', methods=['POST'])
def search_name():
    """Form on homepage to get passed parameter of ticker"""

    # get object from form
    name_object = request.form.get('search_name')

    # query database to get a ticker that matches the search term
    company_query = Company.query.filter(Company.name.ilike('%' + name_object + '%'))
    # create a list to iterate over on the results page
    company_list = list(map(Company.details, company_query))

    # dictionary object to render results on HTML page
    response = {
        'count': len(company_list),
        'data': company_list
    }

    return render_template('pages/search_company.html', results=response, search_term=name_object)


@app.route('/company/<company_id>')
def show_company(company_id):
    """Display a company's information on a web page."""

    # get id of the specified company
    company_query = Company.query.get(company_id)

    if company_query:
        # call company detail method to get dictionary object
        company_details = Company.details(company_query)

        # return to HTML page of company and send data
        return render_template('pages/show_company.html', company=company_details)
    # check query

    else:
        return render_template('errors/404.html')


@app.route('/about')
def about_us():
    """Static webpage about Joe, Ciaran, and why use Coja"""
    return render_template('pages/about.html')


@app.route('/headers', methods=['GET'])
def company():
    name = 'Apple'
    print(name)
    return{'company': name}


