__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

from flask.ext.wtf import Form
from wtforms import StringField, SelectField, BooleanField, HiddenField, IntegerField, FloatField, DecimalField
from wtforms.validators import DataRequired, Optional


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
    server_temp_proc_max_temp_limit = FloatField("server_temp_proc_max_temp_limit")
    temperature_back_plot_period = IntegerField("temperature_back_plot_period")
    temperature_scan_period = FloatField("temperature_scan_period")


class BackPeriodForm(Form):
    back_period = IntegerField('back_period')


class HeatConsumptionInput(Form):
    kitchen_status = IntegerField("kitchen_status", validators=[Optional()])
    hallway_status = IntegerField("hallway_status", validators=[Optional()])
    bathroom_status = IntegerField("bathroom_status", validators=[Optional()])
    room_status = IntegerField("room_status", validators=[Optional()])

    kitchen_radiator = FloatField("kitchen_radiator", validators=[Optional()])
    hallway_radiator = FloatField("hallway_radiator", validators=[Optional()])
    bathroom_radiator = FloatField("bathroom_radiator", validators=[Optional()])
    room_radiator = FloatField("room_radiator", validators=[Optional()])


class WaterConsumption(Form):
    hot = FloatField("hot water", validators=[Optional()])
    cold = FloatField("cold water", validators=[Optional()])
