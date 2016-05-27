from BeautifulSoup import BeautifulSoup
from sqlalchemy import create_engine
from collections import namedtuple
from pprint import pprint
import datetime
import requests
import socket
import time

import sys

sys.path.append("../..")
from app.common.net import is_up

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


def get_last_ljubljana_weather():
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


def get_last_location_weather(location="Ljubljana"):
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


def ping_all(engine):
    print "\nStarting pinger"
    _ip = 2
    _id = 0

    with engine.connect() as con:
        # Get node information
        d = con.execute("SELECT nodes.id AS nodes_id, nodes.name AS nodes_name, nodes.ip AS nodes_ip FROM nodes WHERE nodes.in_use != FALSE;")
        nodes = d.fetchall()

        # Get + calculate new common id
        d = con.execute("SELECT last_entry.last_common_id AS last_entry_last_common_id FROM last_entry ORDER BY last_entry.date_time DESC LIMIT 1;")
        common_id = d.fetchall()[0][0] + 1

        # Insert new common id
        d = con.execute("INSERT INTO last_entry (date_time, last_common_id, ready_to_read) VALUES (%s, %s, %s)",
                        (datetime.datetime.today(), common_id, "FALSE"))

    # Ping nodes
    for node in nodes:
        print "Pinging:", node[_ip]
        try:
            up, delay = is_up(node[_ip], timeout=0.9)
        except socket.gaierror:
            up, delay = False, None
        with engine.connect() as con:
            # Insert new ping data
            d = con.execute("INSERT INTO pinger_data (date_time, common_id, up, node_id, delay) VALUES (%s,%s,%s,%s,%s)",
                            (datetime.datetime.today(), common_id, up, node[_id], delay))
    with engine.connect() as con:
        # Update last common entry so it can be read
        d = con.execute("UPDATE last_entry SET ready_to_read=%s WHERE last_common_id=%s", ("TRUE", common_id))


def arso_weather(engine):
    print "\nStarting ARSO weather\n"
    # ids:
    #  - 44         , 45      , 46
    #  - temperature, humidity, solar radiation

    weather_1 = get_last_ljubljana_weather()
    w_1_update_time = " ".join(weather_1.valid.split(" ")[0:2])
    w_1_update_time = datetime.datetime.strptime(w_1_update_time, "%d.%m.%Y %H:%M")
    print "ARSO update time:", w_1_update_time

    with engine.connect() as con:
        # Get previous update time
        d = con.execute("""
        SELECT sensor_data.date_time
        FROM sensor_data
        WHERE sensor_data.sensor_id = 44
        ORDER BY sensor_data.date_time DESC
        LIMIT 1;
        """)
        previous_update_time = d.first()
    print "Previous db update time:", previous_update_time

    if previous_update_time is None or previous_update_time[0] < w_1_update_time:
        print "Will save ARSO data to database", w_1_update_time
        pprint(weather_1)
        with engine.connect() as con:
            # Insert temperature data
            d = con.execute("""
            INSERT INTO sensor_data (sensor_id, date_time, value, unit)
            VALUES (%s,%s,%s,%s);
            """, (44, w_1_update_time, float(weather_1.temperature), "C"))

            # Insert humidity data
            d = con.execute("""
            INSERT INTO sensor_data (sensor_id, date_time, value, unit)
            VALUES (%s,%s,%s,%s);
            """, (45, w_1_update_time, float(weather_1.humidity), "%"))

            # Insert solar radiation data
            d = con.execute("""
            INSERT INTO sensor_data (sensor_id, date_time, value, unit)
            VALUES (%s,%s,%s,%s);
            """, (46, w_1_update_time, float(weather_1.sun_radiation), "W/m2"))

            # Insert air pressure data
            d = con.execute("""
            INSERT INTO sensor_data (sensor_id, date_time, value, unit)
            VALUES (%s,%s,%s,%s);
            """, (51, w_1_update_time, float(weather_1.air_pressure), "hPa"))

            # Real air pressure data
            d = con.execute("""
            INSERT INTO sensor_data (sensor_id, date_time, value, unit)
            VALUES (%s,%s,%s,%s);
            """, (52, w_1_update_time, float(weather_1.real_air_pressure), "hPa"))
    else:
        print "Will NOT save ARSO data to database"


def main_looper(engine):
    print "Starting main looper"
    # First initial ping and ARSO
    ping_all(engine)
    arso_weather(engine)

    with engine.connect() as con:
        # Get pinger scan time
        d = con.execute("SELECT value FROM app_settings WHERE name = 'PINGER_SCAN_PERIOD';")
        pinger_scan_period = d.first()
        pinger_scan_period = float(pinger_scan_period[0])

        d = con.execute("SELECT value FROM app_settings WHERE name = 'ARSO_SCAN_PERIOD';")
        arso_scan_period = d.first()
        arso_scan_period = float(arso_scan_period[0])
    print "Pinger_scan_period:", pinger_scan_period
    print "ARSO_scan_period:", arso_scan_period

    pinger_last_time = time.time()
    arso_last_time = time.time()
    while "pigs" != "fly":
        try:
            time_now = time.time()
            if (pinger_last_time + pinger_scan_period) < time_now:
                ping_all(engine)
                print "\nPinger_scan_period:", pinger_scan_period
                with engine.connect() as con:
                    # Get pinger scan time
                    d = con.execute("SELECT value FROM app_settings WHERE name = 'PINGER_SCAN_PERIOD';")
                    pinger_scan_period = d.first()
                    pinger_scan_period = float(pinger_scan_period[0])
                pinger_last_time = time_now

            if (arso_last_time + arso_scan_period) < time_now:
                arso_weather(engine)
                print "\nARSO_scan_period:", arso_scan_period
                with engine.connect() as con:
                    # Get ARSO scan time
                    d = con.execute("SELECT value FROM app_settings WHERE name = 'ARSO_SCAN_PERIOD';")
                    arso_scan_period = d.first()
                    arso_scan_period = float(arso_scan_period[0])
                arso_last_time = time_now
        except Exception as exc:
            with open("LOOPER_ERROR.log", "a") as error_log:
                error_log.write("exc: {0}\nexc.message: {1}\nexc.args: {2}".format(exc,
                                                                                   exc.message,
                                                                                   exc.args))
            print exc
            print exc.message
            print exc.args
        time.sleep(1)


if __name__ == '__main__':
    eng = create_engine('postgresql://lesko:ma19ne99@192.168.1.99/homeNET')
    main_looper(eng)
    # arso_weather(eng)

    # with eng.connect() as con:
    #     # Get previous update time
    #     d = con.execute("""
    #         INSERT INTO sensor_data (sensor_id, date_time, value, unit)
    #         VALUES (%s,%s,%s,%s);
    #         """, (500, datetime.datetime.today(), float(1111), "EH"))
