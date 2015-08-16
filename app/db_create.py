__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

from app import db
from app.models import Nodes, LastEntry
import sqlalchemy

import datetime


def add_nodes():
    data = [
        Nodes(name="Router gateway", ip="192.168.1.1", interface="physical"),
        Nodes(name="Neva", ip="192.168.1.50", laptop=True, interface="physical"),
        Nodes(name="Lesko", ip="192.168.1.51", laptop=True, interface="physical"),
        Nodes(name="ServerBBB", ip="192.168.1.52", interface="physical"),
        Nodes(name="Virtual Ubuntu", ip="192.168.1.53", interface="physical"),
        Nodes(name="NAS", ip="192.168.1.100", interface="physical"),
        Nodes(name="Rigol - Oscilloscope", ip="192.168.1.200", interface="physical"),
        Nodes(name="Server234", ip="192.168.1.234", laptop=True, interface="physical"),

        Nodes(name="Router - gateway", ip="192.168.2.1", interface="WiFi"),
        Nodes(name="Neva phone", ip="192.168.2.3", handheld=True, interface="WiFi"),
        Nodes(name="Neva PC", ip="192.168.2.4", laptop=True, interface="WiFi"),
        Nodes(name="Lesko phone", ip="192.168.2.5", handheld=True, interface="WiFi"),
    ]
    for node in data:
        try:
            db.session.add(node)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
                print "Not adding nodes"


def add_first_last_entry():
    data = LastEntry(datetime.datetime.today(), 0)
    try:
        db.session.add(data)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
            print "Not adding nodes"

if __name__ == '__main__':

    # db.create_all()
    add_nodes()
    # add_first_last_entry()
