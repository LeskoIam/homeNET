from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

app = Flask(__name__)
app.config.from_object('real_config')

db = SQLAlchemy(app)

from app import models
from app.views import views

# Add custom jinja filters
import custom_jinja_filters

app.jinja_env.filters["format_datetime"] = custom_jinja_filters.format_datetime
