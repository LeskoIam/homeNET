from flask import render_template, Blueprint, jsonify
from app.models import LastEntry, Nodes, PingerData
from app import db

import requests
from collections import namedtuple
from BeautifulSoup import BeautifulSoup

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('aggregator_blueprint', __name__, template_folder='templates')


@blueprint.route("/aggregator")
def view_aggregator():  # aggregator
    weather_1 = get_last_location_weather()
    weather_2 = get_location_weather("Ljubljana")

    return render_template("aggregator.html",
                           weather_1=weather_1,
                           weather_2=weather_2,
                           page_loc="aggregator")


#############
# ##     ## #
#    API    #
# ##     ## #
#############

@blueprint.route("/api/network_summary")
def get_network_summary():
    # Out of M nodes (n_all_nodes) N are active (pinged) and U nodes are up
    n_all_nodes = db.session.query(
            db.func.count(Nodes.id)).one()[0]

    n_all_active_nodes = db.session.query(
            db.func.count(Nodes.id)).\
        filter(Nodes.in_use == True).one()[0]

    last_common_id = db.session.query(
            LastEntry.last_common_id).\
        filter(LastEntry.ready_to_read == True). \
        order_by(LastEntry.date_time.desc()).first()[0]

    n_all_up_nodes = db.session.query(
            db.func.count(PingerData.id)).\
        filter(Nodes.id == PingerData.node_id). \
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


#############
# ##     ## #
#    ???    #
# ##     ## #
#############

def get_last_location_weather():
    """

    :return:
        .valid               - date
        .clouds              - img url
        .temperature         - C
        .humidity            - %
        .wind_speed          - km/h
        .wind_direction      - img url
        .wind_gust_speed     - km/h
        .air_pressure        - hPa
        .real_air_pressure   - hPa
        .rain                - mm
        .sum_rain            - mm
        .sun_radiation       - W/m2
        .sun_radiation_diff  - W/m2
        .water_temperature   - C
    """
    base_url = "http://meteo.arso.gov.si"
    address = "http://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observationAms_LJUBL-ANA_BEZIGRAD_history.html"
    page = requests.get(address)
    html = page.content
    parsed_html = BeautifulSoup(html)

    data = parsed_html.find("table", attrs={"class": "meteoSI-table"})

    a = namedtuple("arso_weather", ("valid",               # 1   -  0
                                    "clouds",              # 8
                                    "temperature",         # 10
                                    "humidity",            # 12
                                    "wind_speed",          # 14
                                    "wind_direction",      # 16  -  5
                                    "wind_gust_speed",     # 18
                                    "air_pressure",        # 20
                                    "real_air_pressure",   # 22
                                    "rain",                # 24
                                    "sum_rain",            # 26  -  10
                                    "sun_radiation",       # 28
                                    "sun_radiation_diff",  # 30
                                    "water_temperature"))  # 32  -  13

    data_ = data.findAll("tr")[1].findAll("td")
    data = [data_[x].string for x in [10, 12, 14, 18, 20, 22, 24, 26, 28, 30, 32]]
    # 1, 8, 16
    # 0, 1, 5
    data.insert(0, data_[1].string)

    clouds_image = data_[8].find("img")
    if clouds_image is not None:
        data.insert(1, base_url + clouds_image["src"])
    else:
        data.insert(1, None)
    data.insert(5, base_url + data_[16].find("img")["src"])

    return a(*data)


def get_location_weather(location="Ljubljana"):
    """Get weather information from ARSOs
    automatic weather stations.

    :param location: location to get observations for
    :return: namedtuple object with
        .temperature    - C
        .humidity       - %
        .wind_direction - [N, S, E, W]
        .wind_speed     - m/s
        .wind_gusts     - m/s
        .air_pressure   - hPa
        .rain           - mm
        .sun_radiation  - W/m2
    """
    address = "http://www.arso.gov.si/vreme/napovedi%20in%20podatki/vreme_avt.html"
    page = requests.get(address)
    html = page.content

    parsed_html = BeautifulSoup(html)

    station_data = parsed_html.find("table", attrs={"class": "online"})
    station_names = [x.string for x in station_data.findAll("td", attrs={"class": "onlineimena"})]
    station_data = [x for x in station_data.findAll("tr")]
    print station_names
    datad = namedtuple("location_weather", ("temperature",
                                            "humidity",
                                            "wind_direction",
                                            "wind_speed",
                                            "wind_gusts",
                                            "air_pressure",
                                            "rain",
                                            "sun_radiation"))
    for i, station_name in enumerate(station_names):
        if station_name.lower() == location.lower():
            print station_name
            data = [x.string for x in station_data[i + 2].findAll("td")]
            data = data[1:]
            d = datad(data[0], data[1], slo_to_eng_compass(data[2]), data[3], data[5], *data[7:])
            return d


def slo_to_eng_compass(eng_str):
    eng_str = eng_str.upper()
    compass_mapping = {"S": "N",
                       "J": "S",
                       "V": "E",
                       "Z": "W"}
    out = ""
    for c in eng_str:
        out += compass_mapping[c.upper()]
    return out
