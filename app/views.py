__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
from flask import render_template, request, redirect, flash, jsonify
from app import app, db
import sqlalchemy
from flask.ext.basicauth import BasicAuth

from models import PingerData, LastEntry, Nodes
from forms import AddNodeForm

basic_auth = BasicAuth(app)


@app.route('/table', methods=["GET", "POST"])
def show():
    last_common_id, update_time = db.session.query(LastEntry.last_common_id, LastEntry.date_time). \
        order_by(LastEntry.date_time.desc()).first()

    data = db.session.query(PingerData.up, Nodes.id, Nodes.name, Nodes.ip, Nodes.interface).join(Nodes). \
        filter(PingerData.common_id == last_common_id).order_by(Nodes.id.asc()).all()

    last_up_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == 1).group_by(PingerData.node_id).all()

    last_down_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == 0).group_by(PingerData.node_id).all()

    mean_delay = db.session.query(PingerData.node_id,
                                  (db.func.sum(PingerData.delay) / db.func.count(PingerData.delay)) * 1000). \
        filter(PingerData.delay != None). \
        group_by(PingerData.node_id).all()

    for d in data:
        d.last_up = find_in_lists(last_up_time, d.id, 0)
        d.last_down = find_in_lists(last_down_time, d.id, 0)
        d.mean_delay = find_in_lists(mean_delay, d.id, 0)

    # print last_up_time
    # print last_down_time
    # print mean_delay

    return render_template("view_devices_table.html",
                           data=data,
                           update_time=update_time)


@app.route("/manage_devices", methods=["GET", "POST"])
def manage_device():
    all_devices = db.session.query(Nodes).order_by(Nodes.id.asc()).all()
    # print all_devices
    # print request.form
    return render_template("manage_devices.html", all_devices=all_devices)


@app.route("/delete/<device_id>", methods=["GET", "POST"])
def delete_device(device_id):
    print "delete row"
    to_delete = db.session.query(Nodes).filter(Nodes.id == int(device_id)).all()[0]
    print to_delete
    db.session.delete(to_delete)
    db.session.commit()
    flash("Successfully deleted {0}".format(str(to_delete)))
    return redirect("/manage_devices")


@app.route("/add_device", methods=["GET", "POST"])
def add_device():
    form = AddNodeForm()
    if form.validate_on_submit():
        print form.device_type.data
        print "All is valid"
        to_add = Nodes(name=form.name.data,
                       ip=form.ip.data,
                       interface=form.interface.data,
                       device_type=form.device_type.data if form.device_type.data != "None" else None)
        try:
            db.session.add(to_add)
            db.session.commit()
            flash("Device successfully added!")
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not adding nodes - %s" % str(e.message))
        return redirect("/manage_devices")
    else:
        flash("Form missing data!")
    return render_template("add_device.html", form=form)


@app.route("/edit/<device_id>", methods=["GET", "POST"])
def edit_device(device_id):
    pass


@app.route('/temp', methods=["GET", "POST"])
def test():
    return render_template("view_devices_table.html")


def find_in_lists(data, search, index):
    for d in data:
        if d[index] == search:
            return d
    return None
