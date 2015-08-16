__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# WTforms
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')

BASIC_AUTH_FORCE = True
BASIC_AUTH_USERNAME = "lesko"
BASIC_AUTH_PASSWORD = "1234"
