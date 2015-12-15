# coding=utf-8
from flask import render_template, Blueprint, jsonify, flash, redirect
from app.models import SensorData, Sensors
from app.forms import BackPeriodForm, HeatConsumptionInput, WaterConsumption
from ..common import get_setting, time_since_epoch
from app.common import stats
from app import db
import time

import datetime
from collections import namedtuple

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('environment_blueprint', __name__, template_folder='templates')


@blueprint.route("/environment", methods=["GET", "POST"])
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


@blueprint.route("/heating", methods=['GET', 'POST'])
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
        a = namedtuple("set_point", ("data", "percent"))
        a.data = data
        a.percent = data.value / (0.01 * 5)
        data_out.append(a)
    sum_percent = sum([x.percent for x in data_out]) / len(data_out)
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


@blueprint.route("/water", methods=['GET', 'POST'])
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
        return redirect('/water')

    return render_template("water.html",
                           form=form,
                           page_loc="water")


#############
# ##     ## #
#    API    #
# ##     ## #
#############

@blueprint.route("/api/heating_data")
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


@blueprint.route("/api/consumption_data")
def get_consumption_data():
    all_heating_sensors = db.session.query(Sensors.id, Sensors.location). \
        filter(Sensors.id.in_((2, 3, 4, 5))).order_by(Sensors.id.asc()).all()

    consumption_per_room = []
    sum_consumption = None
    max_iter = len(all_heating_sensors) - 1
    for i, s in enumerate(all_heating_sensors):
        data = db.session.query(Sensors.location, SensorData.date_time, SensorData.value). \
            filter(Sensors.id == SensorData.sensor_id). \
            filter(SensorData.sensor_id == s.id).order_by(SensorData.date_time.asc()).all()

        time_ = [time_since_epoch(x.date_time) * 1000 for x in data]
        data_ = [x.value for x in data]
        diff_data_ = stats.diff([x.value for x in data])

        if i == 0:
            sum_consumption = diff_data_
        else:
            sum_consumption = [sum(x) for x in zip(sum_consumption, diff_data_)]

        diff_data_ = zip(time_[1:], diff_data_)
        data_ = zip(time_, data_)
        if max_iter == i:
            # If last iteration
            sum_consumption = zip(time_[1:], sum_consumption)

        out = [
            {
                "name": data[0].location.capitalize(),
                "data": data_
            },
            {
                "name": data[0].location.capitalize() + " consumption",
                "data": diff_data_
            }
        ]

        consumption_per_room.append(out)

    print consumption_per_room
    print sum_consumption

    sum_consumption = [
            {
                "name": "sum cons",
                "data": sum_consumption
            }]
    data_per_room = db.session.query(SensorData.date_time, SensorData.value, SensorData.sensor_id,
                                     Sensors.location).join(Sensors). \
        filter(Sensors.id == SensorData.sensor_id).filter(Sensors.id == s.id). \
        order_by(SensorData.date_time.desc()).first()
    timestamp_str = data_per_room.date_time  # TODO. Update time for every single sensor
    series = {"consumption_per_room": consumption_per_room,
              "status_last_update_time": datetime.datetime.strftime(timestamp_str, "%d.%m.%Y %H:%M:%S"),
              "sum_consumption": sum_consumption
              }
    return jsonify(**series)



@blueprint.route("/api/water_data")
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


@blueprint.route("/api/temperature_data")
@blueprint.route("/api/temperature_data/<back_period>")
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
    scan_period = get_setting("TEMPERATURE_SCAN_PERIOD", float)
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
        "last_update_time": datetime.datetime.strftime(timestamp_str, "%d.%m.%Y %H:%M:%S"),
        "scan_period": scan_period.value
    }
    # print series["data"]
    return jsonify(**series)
