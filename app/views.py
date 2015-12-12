# coding=utf-8
from flask import render_template, redirect, flash, request, jsonify
# from flask.ext.basicauth import BasicAuth
import sqlalchemy
from forms import AddEditNodeForm, SettingsForm, BackPeriodForm
from forms import HeatConsumptionInput, WaterConsumption
from models import PingerData, LastEntry, Nodes, AppSettings, SensorData, Sensors
from common import stats
from app import app, db
from StringIO import StringIO
from pprint import pprint
import datetime
import csv
import os
from collections import namedtuple

__author__ = 'Lesko'


# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

# basic_auth = BasicAuth(app)


@app.errorhandler(404)
def page_not_found(e):
    """Handles when unknown address is requested.

    :param e: error code description
    :return: response
    """
    return render_template('404.html',
                           page_loc="404"), 404


@app.route('/')
@app.route('/home')
def home():
    """Render homepage.

    :return: response
    """
    return render_template("home.html", page_loc="home")


@app.route('/view_nodes', methods=["GET", "POST"])
def view_nodes():
    """Show network nodes and their status.

    :return: response
    """
    # LastEntry.ready_to_read == True, to ensure no partial pinger data is displayed.
    last_common_id, update_time = db.session.query(LastEntry.last_common_id, LastEntry.date_time). \
        filter(LastEntry.ready_to_read == True). \
        order_by(LastEntry.date_time.desc()).first()

    data = db.session.query(PingerData.up, Nodes.id, Nodes.name, Nodes.ip, Nodes.interface, Nodes.node_type).join(
            Nodes). \
        filter(PingerData.common_id == last_common_id). \
        filter(Nodes.in_use != False).order_by(Nodes.id.asc()).all()  # TODO: == True?

    return render_template("view_nodes.html",
                           data=data,
                           update_time=update_time,
                           page_loc="nodes - view")


@app.route("/node_details/<node_id>", methods=["GET", "POST"])
def show_node_details(node_id=None):
    """Show node details page filed with specific (node_id) information.

    :param node_id: id of the node
    :return: response
    """
    node_name = db.session.query(Nodes.name).filter(Nodes.id == node_id).first()[0]

    last_up_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == "TRUE").filter(PingerData.node_id == node_id). \
        order_by(PingerData.date_time.desc()).first()
    pprint(last_up_time)

    last_down_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == "FALSE").filter(PingerData.node_id == node_id). \
        order_by(PingerData.date_time.desc()).first()
    pprint(last_down_time)

    # Calculate mean with SQL
    mean_delay = db.session.query(PingerData.node_id,
                                  (db.func.sum(PingerData.delay) / db.func.count(PingerData.delay)) * 1000). \
        filter(PingerData.delay != None).filter(PingerData.node_id == node_id). \
        group_by(PingerData.node_id).all()
    # pprint(mean_delay)

    try:
        last_up_time = last_up_time[1]
    except (IndexError, TypeError):
        last_up_time = None

    try:
        last_down_time = last_down_time[1]
    except (IndexError, TypeError):
        last_down_time = None
    try:
        mean_delay = mean_delay[0][1]
    except IndexError:
        mean_delay = None
    return render_template("node_details.html",
                           node_id=node_id,
                           node_name=node_name,
                           last_up_time=last_up_time,
                           last_down_time=last_down_time,
                           mean_delay=mean_delay,
                           page_loc="nodes - details")


@app.route("/manage_nodes", methods=["GET", "POST"])
def manage_nodes():
    """Show manage mode view. Nodes can be deleted, added,
     edited in this view.

    :return: response
    """
    all_nodes = db.session.query(Nodes).order_by(Nodes.id.asc()).all()
    return render_template("manage_nodes.html",
                           all_nodes=all_nodes,
                           page_loc="nodes - manage")


@app.route("/add_node", methods=["GET", "POST"])
def add_node():
    """Add node dialog.

    :return: response
    """
    form = AddEditNodeForm()
    if form.validate_on_submit():
        # print form.device_type.data
        # print "All is valid"
        # print form.in_use.data
        to_add = Nodes(name=form.name.data,
                       ip=form.ip.data,
                       interface=form.interface.data,
                       node_type=form.node_type.data if form.node_type.data != "None" else None,
                       in_use=form.in_use.data)
        try:
            db.session.add(to_add)
            db.session.commit()
            flash("Successfully added {0}".format(str(to_add)))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not adding nodes - %s" % str(e.message))
        return redirect("/manage_nodes")
    return render_template("add_edit_node.html",
                           form=form,
                           add_edit="add node",
                           page_loc="node - add")


@app.route("/edit/<node_id>", methods=["GET", "POST"])
def edit_node(node_id):
    """Node information can be edited in this view.

    :param node_id: id of the node to be edited
    :return: response
    """
    try:
        to_edit = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
    except IndexError:
        flash("Edit not successful!")
        return redirect("/manage_nodes")
    form = AddEditNodeForm()
    if form.validate_on_submit():
        print "Edit form Valid"
        to_edit.name = form.name.data
        to_edit.ip = form.ip.data
        to_edit.interface = form.interface.data
        to_edit.node_type = form.node_type.data if form.node_type.data != "None" else None
        to_edit.in_use = form.in_use.data
        try:
            db.session.commit()
            flash("Successfully edited {0}".format(str(to_edit)))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not editing nodes - %s" % str(e.message))
        return redirect("/manage_nodes")

    form.name.data = to_edit.name
    form.ip.data = to_edit.ip
    form.interface.data = to_edit.interface
    form.node_type.data = to_edit.node_type
    form.in_use.data = to_edit.in_use
    form.node_id = to_edit.id
    return render_template("add_edit_node.html",
                           form=form,
                           add_edit="edit node",
                           page_loc="nodes - edit")


@app.route("/toggle_node_in_use/<node_id>", methods=["GET", "POST"])
def toggle_node_in_use(node_id):
    """Toggles visible nodes.

    :param node_id: id of the node to be toggled
    :return: redirect
    """
    print "Toggle row"
    try:
        to_toggle = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
    except IndexError:
        flash("Toggle not successful!")
        return redirect("/manage_nodes")
    # print to_toggle
    to_toggle.in_use = not to_toggle.in_use
    try:
        db.session.commit()
        # flash("Successfully toggled {0}".format(str(to_toggle)))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print e
        flash("Toggle not successful - %s" % str(e.message))
    return redirect("/manage_nodes")


@app.route("/delete/<node_id>", methods=["GET", "POST"])
def delete_node(node_id):
    print "delete row"
    try:
        to_delete = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
        # data_to_delete = db.session.query(PingerData).filter(PingerData.node_id == node_id).all()
    except IndexError:
        flash("Delete not successful!")
        return redirect("/manage_nodes")
    # print to_delete
    try:
        db.session.delete(to_delete)
        # for data in data_to_delete:
        #     db.session.delete(data)
        db.session.commit()
        flash("Successfully deleted {0} and it's data".format(str(to_delete)))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print e
        flash("Delete not successful - %s" % str(e.message))
    return redirect("/manage_nodes")


@app.route("/settings", methods=["GET", "POST"])
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
        flash("Settings successfully changed!")
    details_plot_back_period = get_setting("NODE_DETAILS_PLOT_BACK_PERIOD", int)
    server_temp_plot_back_period = get_setting("SERVER_TEMP_PLOT_BACK_PERIOD", int)
    server_temp_proc_max_temp_limit = get_setting("PROC_MAX_TEMP_LIMIT", float)
    temperature_plot_back_period = get_setting("TEMPERATURE_BACK_PLOT_PERIOD", int)

    form.node_details_plot_back_period.data = details_plot_back_period.value
    form.server_temp_plot_back_period.data = server_temp_plot_back_period.value
    form.server_temp_proc_max_temp_limit.data = server_temp_proc_max_temp_limit.value
    form.temperature_back_plot_period.data = temperature_plot_back_period.value
    return render_template("settings.html",
                           form=form,
                           page_loc="settings")


@app.route("/aggregator")
def view_aggregator():
    return render_template("aggregator.html",
                           page_loc="aggregator")


@app.route("/heating", methods=['GET', 'POST'])
def heating():
    form = HeatConsumptionInput()
    if form.validate_on_submit():
        unit = "e"
        timestamp = datetime.datetime.today()

        # Status
        # Kitchen
        if form.kitchen_status.data is not None:
            sensor_id = 2
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.kitchen_status.data,
                              unit=unit)
            db.session.add(data)
        # Hallway
        if form.hallway_status.data is not None:
            sensor_id = 3
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.hallway_status.data,
                              unit=unit)
            db.session.add(data)
        # Bathroom
        if form.bathroom_status.data is not None:
            sensor_id = 4
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.bathroom_status.data,
                              unit=unit)
            db.session.add(data)
        # Room
        if form.room_status.data is not None:
            sensor_id = 5
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.room_status.data,
                              unit=unit)
            db.session.add(data)

        # Radiator
        # Kitchen
        if form.kitchen_radiator.data is not None:
            sensor_id = 8
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.kitchen_radiator.data,
                              unit=unit)
            db.session.add(data)
        # Hallway
        if form.hallway_radiator.data is not None:
            sensor_id = 9
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.hallway_radiator.data,
                              unit=unit)
            db.session.add(data)
        # Bathroom
        if form.bathroom_radiator.data is not None:
            sensor_id = 10
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.bathroom_radiator.data,
                              unit=unit)
            db.session.add(data)
        # Room
        if form.room_radiator.data is not None:
            sensor_id = 11
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.room_radiator.data,
                              unit=unit)
            db.session.add(data)

        db.session.commit()
        flash("Successfully entered data!")
        return redirect('/heating')

    # Get radiator valve settings
    all_radiator_settings = db.session.query(Sensors.id, Sensors.location). \
        filter(Sensors.id.in_((8, 9, 10, 11))).order_by(Sensors.id.asc()).all()
    data_out = []
    for s in all_radiator_settings:
        data = db.session.query(SensorData.date_time, SensorData.value, SensorData.sensor_id, Sensors.location).join(
                Sensors). \
            filter(Sensors.id == SensorData.sensor_id).filter(Sensors.id == s.id). \
            order_by(SensorData.date_time.desc()).first()
        # data.__dict__["percent"] = data.value/(0.01*5)
        a = namedtuple("set_point", ("data", "percent"))
        a.data = data
        a.percent = data.value / (0.01 * 5)
        data_out.append(a)
    sum_percent = sum([x.percent for x in data_out])/len(data_out)
    sum_setting = sum([x.data.value for x in data_out])
    print sum_percent, sum_setting
    timestamp_str = data.date_time  # TODO. Update time for every single sensor

    return render_template("heating.html",
                           form=form,
                           radiator_data=data_out,
                           radiator_sum_percent=sum_percent,
                           radiator_sum_setting=sum_setting,
                           settings_last_update_time=timestamp_str,
                           page_loc="heating")


@app.route("/water", methods=['GET', 'POST'])
def water():
    form = WaterConsumption()
    if form.validate_on_submit():
        unit = "m3"
        timestamp = datetime.datetime.today()

        # Hot water
        if form.hot.data is not None:
            sensor_id = 7
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.hot.data,
                              unit=unit)
            db.session.add(data)
        # Cold Water
        if form.cold.data is not None:
            sensor_id = 6
            data = SensorData(sensor_id=sensor_id,
                              date_time=timestamp,
                              value=form.cold.data,
                              unit=unit)
            db.session.add(data)

        db.session.commit()
        flash("Successfully entered data!")
        return redirect('/environment')

    return render_template("water.html",
                           form=form,
                           page_loc="water")


@app.route("/environment", methods=["GET", "POST"])
def view_environment():
    form = BackPeriodForm()
    back_period = None
    if form.validate_on_submit():
        print "Form OK 21"
        back_period = form.back_period.data
        print back_period
    back_period = back_period if back_period is not None else get_setting("TEMPERATURE_BACK_PLOT_PERIOD", int).value
    return render_template("environment.html",
                           form=form,
                           page_loc="environment",
                           back_period=back_period)


@app.route("/view_server", methods=["GET", "POST"])
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
    pprint(stat_data)
    return render_template("view_server.html",
                           form=form,
                           back_period=back_period,
                           stat_data=stat_data,
                           limits=limits,
                           update_time=update_time,
                           page_loc="server")


@app.route('/temp', methods=["GET", "POST"])
def test():
    to_delete = db.session.query(PingerData).filter(PingerData.node_id == 2).all()
    # print to_delete
    for data in to_delete:
        db.session.delete(data)
    db.session.commit()
    return render_template("view_nodes.html")


# ###################################################
#                                                   #
#                  API VIEWS                        #
#                                                   #
# ###################################################


@app.route("/api/delay_data/<node_id>")
def get_node_delay_data(node_id=None):
    back_period = get_setting("NODE_DETAILS_PLOT_BACK_PERIOD", int)
    data = db.session.query(PingerData.date_time, PingerData.delay, Nodes.name).join(Nodes). \
        filter(Nodes.id == PingerData.node_id).filter(Nodes.id == node_id). \
        order_by(PingerData.date_time.desc()).limit(back_period.value).all()
    node_data = []
    up_times = []
    down_data = []
    for delay in data:
        node_data.append(delay[1] * 1000 if delay[1] is not None else None)
        up_times.append(time_since_epoch(delay[0]) * 1000)
        down_data.append(-0.01 if delay[1] is None else None)
    # pprint(node_data)
    # pprint(down_data)
    # pprint(up_times)
    series = {"data": [
        {
            "name": "Node Up",
            "data": zip(up_times, node_data)[::-1],
            "color": "green"
        },
        {
            "name": "Node Down",
            "data": zip(up_times, down_data)[::-1],
            "color": "red"
        }
    ],
        "back_period": back_period.value
    }
    # pprint(series)
    return jsonify(**series)


@app.route("/api/heating_data")
def get_heating_data():
    all_heating_sensors = db.session.query(Sensors.id, Sensors.location). \
        filter(Sensors.id.in_((2, 3, 4, 5))).order_by(Sensors.id.asc()).all()
    data_out = []
    for s in all_heating_sensors:
        data = db.session.query(SensorData.date_time, SensorData.value, SensorData.sensor_id, Sensors.location).join(
                Sensors). \
            filter(Sensors.id == SensorData.sensor_id).filter(Sensors.id == s.id). \
            order_by(SensorData.date_time.desc()).first()
        data_out.append({"name": data.location.capitalize(), "y": data.value})
    data_out = sorted(data_out, key=lambda k: k['y'])
    timestamp_str = data.date_time  # TODO. Update time for every single sensor
    series = {"data": data_out,
              "status_last_update_time": datetime.datetime.strftime(timestamp_str, "%d.%m.%Y %H:%M:%S")
              }
    return jsonify(**series)


@app.route("/api/water_data")
def get_water_data():
    colors = {"hot": "red",
              "cold": "blue"}
    m_c = {6: "cold", 7: "hot"}
    all_water_sensors = db.session.query(Sensors.id, Sensors.sensor_type). \
        filter(Sensors.id.in_((6, 7))).all()
    categories = []
    data_out = []
    for s in all_water_sensors:
        print s.id
        data = db.session.query(SensorData.date_time, SensorData.value, SensorData.sensor_id, Sensors.sensor_type). \
            join(Sensors).filter(Sensors.id == SensorData.sensor_id).filter(Sensors.id == s.id). \
            order_by(SensorData.date_time.desc()).first()
        print data
        data_out.append({"y": data.value, "color": colors[m_c[data.sensor_id]]})
        categories.append(data.sensor_type.capitalize())
    timestamp_str = data[0]  # TODO: Update time for every single sensor
    series = {"data": data_out,
              "categories": categories,
              "last_update_time": datetime.datetime.strftime(timestamp_str, "%d.%m.%Y %H:%M:%S")
              }
    # pprint(series)
    return jsonify(**series)


@app.route("/api/server_data")
@app.route("/api/server_data/<back_period>")
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
        # row[0] = datetime.datetime.strptime(row[0], "%H:%M:%S %m/%d/%y")
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


@app.route("/api/temperature_data")
@app.route("/api/temperature_data/<back_period>")
def get_temperature(back_period="None"):
    print back_period, type(back_period), repr(back_period)
    if back_period != "None":
        back_period = int(back_period)
    else:
        back_period = get_setting("TEMPERATURE_BACK_PLOT_PERIOD", int).value

    # For now manually filter data from temperature sensor (is only one for now) "Sensors.id == 1"
    data = db.session.query(SensorData.date_time, SensorData.value).join(Sensors). \
        filter(Sensors.id == SensorData.sensor_id).filter(Sensors.id == 1). \
        order_by(SensorData.date_time.desc()).limit(back_period).all()
    # print "Sensor_data:", data

    temperature_data = []
    timestamp = []
    timestamp_str = data[0][0]
    for temperature in data:
        temperature_data.append(temperature[1] if temperature[1] is not None else None)  # ????
        timestamp.append(time_since_epoch(temperature[0]) * 1000)
    series = {"data": [
        {
            "name": "Temperature °C",
            "data": zip(timestamp, temperature_data)[::-1],
            "color": "green"
        },
    ],
        "back_period": len(temperature_data),
        "last_reading": temperature_data[0],
        "last_hour_average": stats.mean(temperature_data),
        "last_update_time": datetime.datetime.strftime(timestamp_str, "%d.%m.%Y %H:%M:%S")
    }
    return jsonify(**series)


@app.route("/api/network_summary")
def get_network_summary():
    # Out of M nodes (n_all_nodes) N are active (pinged) and U nodes are up
    n_all_nodes = db.session.query(db.func.count(Nodes.id)).one()[0]
    n_all_active_nodes = db.session.query(db.func.count(Nodes.id)).filter(Nodes.in_use == True).one()[0]
    last_common_id = db.session.query(LastEntry.last_common_id).filter(LastEntry.ready_to_read == True). \
        order_by(LastEntry.date_time.desc()).first()[0]
    n_all_up_nodes = db.session.query(db.func.count(PingerData.id)).filter(Nodes.id == PingerData.node_id). \
        filter(PingerData.common_id == last_common_id). \
        filter(PingerData.up == True).one()[0]

    # print n_all_nodes, type(n_all_nodes)
    # print n_all_active_nodes, type(n_all_active_nodes)
    # print last_common_id
    # print n_all_up_nodes

    data = {
        "network": {
            "n_all_nodes": n_all_nodes,
            "n_all_active_nodes": n_all_active_nodes,
            "n_all_up_nodes": n_all_up_nodes
        }
    }
    return jsonify(data)


# ###################################################
#                                                   #
#             HELPER FUNCTIONS & CLASSES            #
#                                                   #
# ###################################################

def delete_node_data(node_id):
    data_to_delete = db.session.query(PingerData).filter(PingerData.node_id == node_id).all()
    # print data_to_delete
    for data in data_to_delete:
        db.session.delete(data)
    db.session.commit()


def find_in_lists(data, search, index):
    for d in data:
        if d[index] == search:
            return d
    return None


class SettingReturn(object):
    def __init__(self, value, default):
        self.value = value
        self.default = default


def get_setting(setting_name, ret_type):
    value = ret_type(db.session.query(AppSettings.value).filter(AppSettings.name == setting_name).first()[0])
    default = ret_type(db.session.query(AppSettings.default_value).filter(AppSettings.name == setting_name).first()[0])
    out = SettingReturn(value=value, default=default)
    return out


def update_setting(setting_name, new_value, ret_type):
    to_update = db.session.query(AppSettings).filter(AppSettings.name == setting_name).first()
    to_update.value = ret_type(new_value)
    db.session.commit()


def time_since_epoch(t):
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()


def remove_non_ascii(mystring):
    out = ""
    for s in mystring:
        try:
            s.decode('ascii')
            out += s
        except UnicodeDecodeError:
            out += " "
    return out


def csv_skip_rows(csv_file, n):
    for a in range(n):
        next(csv_file)


def get_files():
    csv_folder = get_setting("SERVER_TEMP_CSV_FOLDER", str)
    csv_files = []
    files = os.listdir(unicode(csv_folder.value))
    for csv_file in files:
        name, ext = os.path.splitext(csv_file)
        if ext == ".csv":
            csv_files.append(os.path.join(csv_folder.value, csv_file))
    return csv_files


def read_temp_log(files, back_period):
    out = []
    for csv_file_path in files:
        with open(csv_file_path, "rb") as csv_file:
            try:
                hm = tail(csv_file, back_period)
                csv_file = StringIO(hm)
                data = csv.reader(csv_file, delimiter=",")
                for row in data:
                    row = [remove_non_ascii(c) for c in row]
                    wanted = map(int, "0 1 2 3 4 9 14 19 24".split())
                    out_row = []
                    error = False
                    for i in wanted:
                        try:
                            out_row.append(row[i])
                        except IndexError:
                            error = True
                            break
                    if not error:
                        out.append(out_row)
            except ValueError:
                out = []
    out = list(reversed(out))
    out.insert(0, get_setting("SERVER_TEMP_TABLE_HEADER", str).value.split("|"))
    return out


def _tail(f, window=20):
    BUFSIZ = 1024
    f.seek(0, 2)  # move to the end of the file
    bites = f.tell()  # where in the file -> end of file -> file size [bytes]
    size = window
    block = -1
    data = []
    while size > 0 and bites > 0:
        if bites - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from beginning
            f.seek(0, 0)
            # only read what was not read
            data.append(f.read(bites))
        lines_found = data[-1].count('\n')
        size -= lines_found
        bites -= BUFSIZ
        block -= 1
    data.reverse()
    return '\n'.join(''.join(data).splitlines()[-window:])


def tail(f, window=20):
    t = _tail(f, window + 1)
    n, t = t.split("\n", 1)
    return t
