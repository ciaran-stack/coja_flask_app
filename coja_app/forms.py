from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class TickerSearchForm(FlaskForm):
    ticker = StringField('ticker', validators=[DataRequired()])