from flask import render_template, Blueprint, jsonify
from app.forms import BackPeriodForm
from ..common import read_temp_log, get_setting, get_files, time_since_epoch
from app.common import stats
import datetime

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('server_blueprint', __name__, template_folder='templates')


@blueprint.route("/view_server", methods=["GET", "POST"])
def view_server():
    form = BackPeriodForm()
    back_period = None
    if form.validate_on_submit():
        print "Form OK 22"
        back_period = form.back_period.data
        print back_period

    table_data = read_temp_log(get_files(),
                               back_period=back_period if back_period is not None else
                               get_setting("SERVER_TEMP_PLOT_BACK_PERIOD", int).value)

    temperature_chart_data = [[], [], [], []]
    load_chart_data = [[], [], [], []]
    all_date_time = []
    for row in table_data:
        if row[0].startswith("Tim"):
            continue
        date_time = datetime.datetime.strptime(row[0], "%H:%M:%S %m/%d/%y")
        all_date_time.append(date_time)
        temperature_chart_data[0].append(float(row[1]))
        temperature_chart_data[1].append(float(row[2]))
        temperature_chart_data[2].append(float(row[3]))
        temperature_chart_data[3].append(float(row[4]))

        load_chart_data[0].append(float(row[5]))
        load_chart_data[1].append(float(row[6]))
        load_chart_data[2].append(float(row[7]))
        load_chart_data[3].append(float(row[8]))
    update_time = all_date_time[0]
    stat_data = [
        {
            "name": "Core 0",
            "temp_mean": stats.mean(temperature_chart_data[0]),
            "temp_st_dev": stats.st_dev(temperature_chart_data[0]),
            "load_mean": stats.mean(load_chart_data[0]),
            "load_st_dev": stats.st_dev(load_chart_data[0]),
            "temperature_last_reading": temperature_chart_data[0][0]
        },
        {
            "name": "Core 1",
            "temp_mean": stats.mean(temperature_chart_data[1]),
            "temp_st_dev": stats.st_dev(temperature_chart_data[1]),
            "load_mean": stats.mean(load_chart_data[1]),
            "load_st_dev": stats.st_dev(load_chart_data[1]),
            "temperature_last_reading": temperature_chart_data[1][0]
        },
        {
            "name": "Core 2",
            "temp_mean": stats.mean(temperature_chart_data[2]),
            "temp_st_dev": stats.st_dev(temperature_chart_data[2]),
            "load_mean": stats.mean(load_chart_data[2]),
            "load_st_dev": stats.st_dev(load_chart_data[2]),
            "temperature_last_reading": temperature_chart_data[2][0]
        },
        {
            "name": "Core 3",
            "temp_mean": stats.mean(temperature_chart_data[3]),
            "temp_st_dev": stats.st_dev(temperature_chart_data[3]),
            "load_mean": stats.mean(load_chart_data[3]),
            "load_st_dev": stats.st_dev(load_chart_data[3]),
            "temperature_last_reading": temperature_chart_data[3][0]
        },
    ]

    proc_max_temp = get_setting("PROC_MAX_TEMP_LIMIT", float).value
    limits = {"proc_max_temp": proc_max_temp}
    print "lesko", limits
    # pprint(stat_data)
    return render_template("view_server.html",
                           form=form,
                           back_period=back_period,
                           stat_data=stat_data,
                           limits=limits,
                           update_time=update_time,
                           page_loc="server")


#############
# ##     ## #
#    API    #
# ##     ## #
#############

@blueprint.route("/api/server_data")
@blueprint.route("/api/server_data/<back_period>")
def get_server_data(back_period="None"):
    print "get_server_data"
    print back_period, type(back_period), repr(back_period)
    if back_period != "None":
        back_period = int(back_period)
    else:
        back_period = get_setting("SERVER_TEMP_PLOT_BACK_PERIOD", int).value
    table_data = read_temp_log(get_files(),
                               back_period=back_period)

    temperature_chart_data = [[], [], [], [], []]
    load_chart_data = [[], [], [], [], []]
    for row in table_data:
        if row[0].startswith("Tim"):
            continue
        # print row[0]
        date_time = datetime.datetime.strptime(row[0], "%H:%M:%S %m/%d/%y")
        temperature_chart_data[0].append(float(row[1]))
        temperature_chart_data[1].append(float(row[2]))
        temperature_chart_data[2].append(float(row[3]))
        temperature_chart_data[3].append(float(row[4]))
        temperature_chart_data[4].append(time_since_epoch(date_time) * 1000)

        load_chart_data[0].append(float(row[5]))
        load_chart_data[1].append(float(row[6]))
        load_chart_data[2].append(float(row[7]))
        load_chart_data[3].append(float(row[8]))
        load_chart_data[4].append(time_since_epoch(date_time) * 1000)

    # print temperature_chart_data[3]
    data = {
        "chart_real_time_temperature": {"data": [
            {
                "name": "Core 0",
                "data": zip(temperature_chart_data[4], temperature_chart_data[0])[::-1]
            },
            {
                "name": "Core 1",
                "data": zip(temperature_chart_data[4], temperature_chart_data[1])[::-1]
            },
            {
                "name": "Core 2",
                "data": zip(temperature_chart_data[4], temperature_chart_data[2])[::-1]
            },
            {
                "name": "Core 3",
                "data": zip(temperature_chart_data[4], temperature_chart_data[3])[::-1]
            }
        ]},

        "chart_real_time_load": {"data": [
            {
                "name": "Core 0",
                "data": zip(load_chart_data[4], load_chart_data[0])[::-1]
            },
            {
                "name": "Core 1",
                "data": zip(load_chart_data[4], load_chart_data[1])[::-1]
            },
            {
                "name": "Core 2",
                "data": zip(load_chart_data[4], load_chart_data[2])[::-1]
            },
            {
                "name": "Core 3",
                "data": zip(load_chart_data[4], load_chart_data[3])[::-1]
            }
        ]},

        "stat_data": {"data": [
            {
                "name": "Core 0",
                "temp_mean": stats.mean(temperature_chart_data[0]),
                "temp_st_dev": stats.st_dev(temperature_chart_data[0]),
                "load_mean": stats.mean(load_chart_data[0]),
                "load_st_dev": stats.st_dev(load_chart_data[0])
            },
            {
                "name": "Core 1",
                "temp_mean": stats.mean(temperature_chart_data[1]),
                "temp_st_dev": stats.st_dev(temperature_chart_data[1]),
                "load_mean": stats.mean(load_chart_data[1]),
                "load_st_dev": stats.st_dev(load_chart_data[1])
            },
            {
                "name": "Core 2",
                "temp_mean": stats.mean(temperature_chart_data[2]),
                "temp_st_dev": stats.st_dev(temperature_chart_data[2]),
                "load_mean": stats.mean(load_chart_data[2]),
                "load_st_dev": stats.st_dev(load_chart_data[2])
            },
            {
                "name": "Core 3",
                "temp_mean": stats.mean(temperature_chart_data[3]),
                "temp_st_dev": stats.st_dev(temperature_chart_data[3]),
                "load_mean": stats.mean(load_chart_data[3]),
                "load_st_dev": stats.st_dev(load_chart_data[3])
            },
        ]}
    }
    return jsonify(**data)
