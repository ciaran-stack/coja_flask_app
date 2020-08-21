from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import Form, StringField, SelectField
import sys
from forms import TickerSearchForm

app = Flask(__name__)

# configure DB by putting user name and local DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://joeyp@localhost:5432/coja'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ciaranmahon@localhost:5432/coja'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Enables migrations of DB changes
migrate = Migrate(app, db)


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



