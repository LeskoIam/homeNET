from flask import render_template, Blueprint, flash
from app.forms import SettingsForm
from ..common import update_setting, get_setting

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('settings_blueprint', __name__, template_folder='templates')


@blueprint.route("/settings", methods=["GET", "POST"])
def view_settings():
    form = SettingsForm()
    if form.validate_on_submit():
        print form.node_details_plot_back_period.data
        update_setting("NODE_DETAILS_PLOT_BACK_PERIOD",
                       form.node_details_plot_back_period.data,
                       int)
        update_setting("SERVER_TEMP_PLOT_BACK_PERIOD",
                       form.server_temp_plot_back_period.data,
                       int)
        update_setting("PROC_MAX_TEMP_LIMIT",
                       form.server_temp_proc_max_temp_limit.data,
                       float)
        update_setting("TEMPERATURE_BACK_PLOT_PERIOD",
                       form.temperature_back_plot_period.data,
                       int)
        update_setting("TEMPERATURE_SCAN_PERIOD",
                       form.temperature_scan_period.data,
                       float)
        flash("Settings successfully changed!")
    details_plot_back_period = get_setting("NODE_DETAILS_PLOT_BACK_PERIOD", int)
    server_temp_plot_back_period = get_setting("SERVER_TEMP_PLOT_BACK_PERIOD", int)
    server_temp_proc_max_temp_limit = get_setting("PROC_MAX_TEMP_LIMIT", float)
    temperature_plot_back_period = get_setting("TEMPERATURE_BACK_PLOT_PERIOD", int)
    temperature_scan_period = get_setting("TEMPERATURE_SCAN_PERIOD", float)

    form.node_details_plot_back_period.data = details_plot_back_period.value
    form.server_temp_plot_back_period.data = server_temp_plot_back_period.value
    form.server_temp_proc_max_temp_limit.data = server_temp_proc_max_temp_limit.value
    form.temperature_back_plot_period.data = temperature_plot_back_period.value
    form.temperature_scan_period.data = temperature_scan_period.value
    return render_template("settings.html",
                           form=form,
                           page_loc="settings")
