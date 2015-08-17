__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
from flask import render_template, redirect, flash
import sqlalchemy
from flask.ext.basicauth import BasicAuth

from app import app, db
from models import PingerData, LastEntry, Nodes
from forms import AddEditNodeForm

basic_auth = BasicAuth(app)


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", page_loc="home")


@app.route('/view_devices', methods=["GET", "POST"])
def show():
    last_common_id, update_time = db.session.query(LastEntry.last_common_id, LastEntry.date_time). \
        order_by(LastEntry.date_time.desc()).first()

    data = db.session.query(PingerData.up, Nodes.id, Nodes.name, Nodes.ip, Nodes.interface).join(Nodes). \
        filter(PingerData.common_id == last_common_id).\
        filter(Nodes.in_use != False).order_by(Nodes.id.asc()).all()

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

    return render_template("view_devices.html",
                           data=data,
                           update_time=update_time,
                           page_loc="devices - view")


@app.route("/manage_devices", methods=["GET", "POST"])
def manage_devices():
    all_devices = db.session.query(Nodes).order_by(Nodes.id.asc()).all()
    return render_template("manage_devices.html",
                           all_devices=all_devices,
                           page_loc="devices - manage")


@app.route("/add_device", methods=["GET", "POST"])
def add_device():
    form = AddEditNodeForm()
    if form.validate_on_submit():
        # print form.device_type.data
        # print "All is valid"
        to_add = Nodes(name=form.name.data,
                       ip=form.ip.data,
                       interface=form.interface.data,
                       device_type=form.device_type.data if form.device_type.data != "None" else None,
                       in_use=True)
        try:
            db.session.add(to_add)
            db.session.commit()
            flash("Device successfully added!")
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not adding nodes - %s" % str(e.message))
        return redirect("/manage_devices")
    return render_template("add_edit_device.html",
                           form=form,
                           add_edit="add device",
                           page_loc="devices - add")


@app.route("/edit/<device_id>", methods=["GET", "POST"])
def edit_device(device_id):
    try:
        to_edit = db.session.query(Nodes).filter(Nodes.id == int(device_id)).all()[0]
    except IndexError:
        flash("Edit not successful!")
        return redirect("/manage_devices")
    form = AddEditNodeForm()
    if form.validate_on_submit():
        print "Edit form Valid"
        to_edit.name = form.name.data
        to_edit.ip = form.ip.data
        to_edit.interface = form.interface.data
        to_edit.device_type = form.device_type.data if form.device_type.data != "None" else None
        to_edit.in_use = form.in_use.data
        try:
            db.session.commit()
            flash("Device successfully edited!")
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not editing nodes - %s" % str(e.message))
        return redirect("/manage_devices")

    form.name.data = to_edit.name
    form.ip.data = to_edit.ip
    form.interface.data = to_edit.interface
    form.device_type.data = to_edit.device_type
    form.in_use.data = to_edit.in_use
    return render_template("add_edit_device.html",
                           form=form,
                           add_edit="edit device",
                           page_loc="devices - edit")


@app.route("/toggle_device_in_use/<device_id>", methods=["GET", "POST"])
def toggle_device_in_use(device_id):
    print "delete row"
    try:
        to_toggle = db.session.query(Nodes).filter(Nodes.id == int(device_id)).all()[0]
    except IndexError:
        flash("Toggle not successful!")
        return redirect("/manage_devices")
    print to_toggle
    to_toggle.in_use = not to_toggle.in_use
    try:
        db.session.commit()
        # flash("Successfully toggled {0}".format(str(to_toggle)))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print e
        flash("Toggle not successful - %s" % str(e.message))
    return redirect("/manage_devices")


@app.route('/temp', methods=["GET", "POST"])
def test():
    # to_delete = db.session.query(PingerData).filter(PingerData.node_id == 2).all()
    # print to_delete
    # for data in to_delete:
    #     db.session.delete(data)
    # db.session.commit()
    return render_template("view_devices.html")


def find_in_lists(data, search, index):
    for d in data:
        if d[index] == search:
            return d
    return None
