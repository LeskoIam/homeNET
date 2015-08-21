__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

from flask.ext.wtf import Form
from wtforms import StringField, SelectField, BooleanField, HiddenField, IntegerField
from wtforms.validators import DataRequired


class AddEditNodeForm(Form):
    name = StringField("name", validators=[DataRequired()])
    ip = StringField("ip", validators=[DataRequired()])
    interface = SelectField("interface", validators=[DataRequired()],
                            choices=[("WiFi", "WiFi"),
                                     ("physical", "Physical")])
    node_type = SelectField('node_type',
                            choices=[("None", "Unknown"),
                                     ("laptop", "Laptop"),
                                     ("handheld", "Handheld"),
                                     ("tower", "Tower"),
                                     ("server", "Server"),
                                     ("web", "Web")])

    in_use = BooleanField("in_use", default=True)
    node_id = HiddenField("node_id")


class SettingsForm(Form):
    node_details_plot_back_period = IntegerField("node_details_plot_back_period")
    server_temp_plot_back_period = IntegerField("server_temp_plot_back_period")
    server_temp_max_table_rows = IntegerField("server_temp_max_table_rows")


class BackPeriodForm(Form):
    back_period = IntegerField('back_period')
