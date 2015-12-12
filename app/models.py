__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
from app import db


class PingerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    date_time = db.Column(db.DateTime, nullable=False)
    common_id = db.Column(db.Integer, nullable=False, index=True)
    up = db.Column(db.Boolean, nullable=False)
    delay = db.Column(db.Float)

    def __init__(self, node_id, date_time, common_id, up, delay=None):
        self.node_id = node_id
        self.date_time = date_time
        self.common_id = common_id
        self.up = up
        self.delay = delay

    def __repr__(self):
        return '<PingerData {}>'.format(self.id)


class LastEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    last_common_id = db.Column(db.Integer, nullable=False, index=True)

    ready_to_read = db.Column(db.Boolean(), nullable=False)

    def __init__(self, date_time, last_common_id, ready_to_read):
        self.date_time = date_time
        self.last_common_id = last_common_id
        self.ready_to_read = ready_to_read

    def __repr__(self):
        return '<LastEntry {0} - {1}>'.format(self.date_time, self.last_common_id)


class Nodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    ip = db.Column(db.String(64), nullable=False, unique=True, index=True)
    interface = db.Column(db.String(64), nullable=False)
    node_type = db.Column(db.String(64))
    in_use = db.Column(db.Boolean(), nullable=False)

    # data_points = db.relationship('PingerData', backref="nodes", lazy='dynamic')

    def __init__(self, name, ip, interface, in_use, node_type=None):
        self.name = name
        self.ip = ip
        self.interface = interface
        self.in_use = in_use
        self.node_type = node_type

    def __repr__(self):
        return '<Nodes {0} - {1}>'.format(self.id, self.name)

    def __str__(self):
        return "{name} - {ip}".format(name=self.name, ip=self.ip)


class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    value_type = db.Column(db.String(16), nullable=False)
    value = db.Column(db.String, nullable=False)
    default_value = db.Column(db.String, nullable=False)

    def __init__(self, name, value_type, value, default_value):
        self.name = name
        self.value_type = value_type
        self.value = value
        self.default_value = default_value

    def __repr__(self):
        return "<AppSettings {0} '{1}': type: <{2}>; value '{3}'>".format(self.id,
                                                                          self.name,
                                                                          self.value_type,
                                                                          self.value)


class Sensors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(128), nullable=False)
    sensor_type = db.Column(db.String(32))

    def __init__(self, location, sensor_type):
        self.location = location
        self.sensor_type = sensor_type

    def __repr__(self):
        return "<Sensor {0} '{1}': type: <{2}>; value '{3}'>".format(self.id,
                                                                     self.location,
                                                                     self.sensor_type)


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))
    date_time = db.Column(db.DateTime, nullable=False)

    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32))

    def __init__(self, sensor_id, date_time, value, unit):
        self.sensor_id = sensor_id
        self.date_time = date_time
        self.value = value
        self.unit = unit

    def __repr__(self):
        return "<SensorData {0} '{1}': type: <{2}>".format(self.id,
                                                           self.value,
                                                           self.unit)
