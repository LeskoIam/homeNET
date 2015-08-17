__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, RadioField
from wtforms.validators import DataRequired


class AddNodeForm(Form):
    name = StringField("name", validators=[DataRequired()])
    ip = StringField("ip", validators=[DataRequired()])
    interface = SelectField("interface", validators=[DataRequired()],
                            choices=[("WiFi", "WiFi"),
                                     ("physical", "Physical")])
    device_type = SelectField('device_type',
                              choices=[("None", "Unknown"),
                                       ("laptop", "Laptop"),
                                       ("handheld", "Handheld"),
                                       ("tower", "Tower"),
                                       ("server", "Server"),
                                       ("web", "Web")])
    # laptop = BooleanField("laptop")
    # tower = BooleanField("tower")
    # handheld = BooleanField("handheld")
