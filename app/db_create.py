from app import db
from app.models import Nodes, LastEntry, AppSettings, Sensors, SensorData
import sqlalchemy

import datetime

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


def add_nodes():
    data = [
        Nodes(name="Router gateway", ip="192.168.1.1", interface="physical", in_use=True),
        Nodes(name="Neva", ip="192.168.1.50", interface="physical", node_type="laptop", in_use=True),
        Nodes(name="Lesko", ip="192.168.1.51", interface="physical", node_type="laptop", in_use=True),
        Nodes(name="ServerBBB", ip="192.168.1.52", interface="physical", in_use=True),
        Nodes(name="Virtual Ubuntu", ip="192.168.1.53", interface="physical", in_use=True),
        Nodes(name="NAS", ip="192.168.1.100", interface="physical", in_use=True),
        Nodes(name="Rigol - Oscilloscope", ip="192.168.1.200", interface="physical", in_use=True),
        Nodes(name="Server234", ip="192.168.1.234", interface="physical", node_type="laptop", in_use=True),
        Nodes(name="Router - gateway", ip="192.168.2.1", interface="WiFi", in_use=True),
        Nodes(name="Neva phone", ip="192.168.2.3", interface="WiFi", node_type="handheld", in_use=True),
        Nodes(name="Neva PC", ip="192.168.2.4", interface="WiFi", node_type="laptop", in_use=True),
        Nodes(name="Lesko phone", ip="192.168.2.5", interface="WiFi", node_type="handheld", in_use=True),
    ]
    for node in data:
        db.session.add(node)
        db.session.commit()


def add_first_last_entry():
    data = LastEntry(datetime.datetime.today(), 0, ready_to_read=True)
    try:
        db.session.add(data)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        print "Not adding nodes"


def add_settings(name, value_type, value, default_value):
    data = AppSettings(name=name,
                       value_type=value_type,
                       value=value,
                       default_value=default_value)
    try:
        db.session.add(data)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        print "Not adding settings"


def add_sensors():
    data = [
        Sensors(location="room",
                sensor_type="temperature",
                sensor_device="DS18B20"),

        Sensors(location="room",
                sensor_type="temperature",
                sensor_device="DS18B20",
                node_id=1),
        Sensors(location="room",
                sensor_type="temperature",
                sensor_device="DHT22",
                node_id=1),
        Sensors(location="room",
                sensor_type="humidity",
                sensor_device="DHT22",
                node_id=1),
        Sensors(location="room",
                sensor_type="light level",
                sensor_device="LDR",
                node_id=1),

        Sensors(location="kitchen",
                sensor_type="heat consumption",
                sensor_device="heat distribution node"),
        Sensors(location="hallway",
                sensor_type="heat consumption",
                sensor_device="heat distribution node"),
        Sensors(location="bathroom",
                sensor_type="heat consumption",
                sensor_device="heat distribution node"),
        Sensors(location="room",
                sensor_type="heat consumption",
                sensor_device="heat distribution node"),

        Sensors(location="hallway",
                sensor_type="cold water consumption",
                sensor_device="measuring dial"),
        Sensors(location="hallway",
                sensor_type="hot water consumption",
                sensor_device="measuring dial"),

        Sensors(location="kitchen",
                sensor_type="radiator setting",
                sensor_device="radiator valve"),
        Sensors(location="hallway",
                sensor_type="radiator setting",
                sensor_device="radiator valve"),
        Sensors(location="bathroom",
                sensor_type="radiator setting",
                sensor_device="radiator valve"),
        Sensors(location="room",
                sensor_type="radiator setting",
                sensor_device="radiator valve"),
    ]
    for d in data:
        try:
            db.session.add(d)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            print "Not adding sensor", d


if __name__ == '__main__':
    db.create_all()
    add_sensors()
    # add_nodes()
    # add_first_last_entry()
    # add_sensors()
    # add_settings("NODE_DETAILS_PLOT_BACK_PERIOD",
    #              "int",
    #              200,
    #              200)
    # add_settings("SERVER_TEMP_PLOT_BACK_PERIOD",
    #              "int",
    #              120,
    #              120)
    # add_settings("SERVER_TEMP_TABLE_HEADER",
    #              "str",
    #              "Time|Core 0 Temp|Core 1 Temp|Core 2 Temp|Core 3 Temp|Core 0 load (%)|Core 1 load (%)|Core 2 load (%)|Core 3 load (%)",
    #              "Time|Core 0 Temp|Core 1 Temp|Core 2 Temp|Core 3 Temp|Core 0 load (%)|Core 1 load (%)|Core 2 load (%)|Core 3 load (%)")
    # add_settings("SERVER_TEMP_CSV_FOLDER",
    #              "str",
    #              "C:\Program Files\Core Temp",
    #              "C:\Program Files\Core Temp")
    # add_settings("PROC_MAX_TEMP_LIMIT",
    #              "float",
    #              80.0,
    #              80.0)
