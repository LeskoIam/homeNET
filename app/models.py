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

    def __init__(self, date_time, last_common_id):
        self.date_time = date_time
        self.last_common_id = last_common_id

    def __repr__(self):
        return '<LastEntry {0} - {1}>'.format(self.date_time, self.last_common_id)


class Nodes(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    ip = db.Column(db.Integer, nullable=False, unique=True, index=True)
    interface = db.Column(db.String(64), nullable=False)

    laptop = db.Column(db.Boolean)
    tower = db.Column(db.Boolean)
    handheld = db.Column(db.Boolean)

    # data_points = db.relationship('PingerData', backref="nodes", lazy='dynamic')

    def __init__(self, name, ip, interface, laptop=None, tower=None, handheld=None):
        self.name = name
        self.ip = ip
        self.interface = interface
        self.laptop = laptop
        self.tower = tower
        self.handheld = handheld

    def __repr__(self):
        return '<Nodes {0} - {1}>'.format(self.id, self.name)
