__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

from app import db
from app.models import Nodes, LastEntry, AppSettings
import sqlalchemy
from sqlalchemy.schema import CreateTable

import datetime


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

if __name__ == '__main__':
    db.create_all()
    add_nodes()
    add_first_last_entry()
    add_settings("NODE_DETAILS_PLOT_BACK_PERIOD",
                 "int",
                 200,
                 200)
    add_settings("SERVER_TEMP_PLOT_BACK_PERIOD",
                 "int",
                 120,
                 120)
    add_settings("SERVER_TEMP_TABLE_HEADER",
                 "str",
                 "Time|Core 0 Temp|Core 1 Temp|Core 2 Temp|Core 3 Temp|Core 0 load (%)|Core 1 load (%)|Core 2 load (%)|Core 3 load (%)",
                 "Time|Core 0 Temp|Core 1 Temp|Core 2 Temp|Core 3 Temp|Core 0 load (%)|Core 1 load (%)|Core 2 load (%)|Core 3 load (%)")
    add_settings("SERVER_TEMP_CSV_FOLDER",
                 "str",
                 "C:\Program Files\Core Temp",
                 "C:\Program Files\Core Temp")
    add_settings("PROC_MAX_TEMP_LIMIT",
                 "float",
                 80.0,
                 80.0)
