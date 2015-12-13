from flask import render_template, Blueprint

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('home_blueprint', __name__, template_folder='templates')


@blueprint.route('/')
@blueprint.route('/home')
def home():
    """Render homepage.

    :return: response
    """
    return render_template("home.html", page_loc="home")
