__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
from flask import render_template, redirect, flash, request, jsonify
import sqlalchemy
from flask.ext.basicauth import BasicAuth

from app import app, db
from models import PingerData, LastEntry, Nodes, AppSettings
from forms import AddEditNodeForm, SettingsForm
from pprint import pprint
import datetime
basic_auth = BasicAuth(app)


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", page_loc="home")


@app.route('/view_nodes', methods=["GET", "POST"])
def view_nodes():
    last_common_id, update_time = db.session.query(LastEntry.last_common_id, LastEntry.date_time). \
        filter(LastEntry.ready_to_read == True). \
        order_by(LastEntry.date_time.desc()).first()

    data = db.session.query(PingerData.up, Nodes.id, Nodes.name, Nodes.ip, Nodes.interface, Nodes.node_type).join(
        Nodes). \
        filter(PingerData.common_id == last_common_id). \
        filter(Nodes.in_use != False).order_by(Nodes.id.asc()).all()  # TODO: == True?

    return render_template("view_nodes.html",
                           data=data,
                           update_time=update_time,
                           page_loc="nodes - view")


@app.route("/node_details/<node_id>", methods=["GET", "POST"])
def show_node_details(node_id=None):
    # print node_id
    node_name = db.session.query(Nodes.name).filter(Nodes.id == node_id).first()[0]
    last_up_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == 1).filter(PingerData.node_id == node_id).group_by(PingerData.node_id).all()
    # pprint(last_up_time)
    last_down_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == 0).filter(PingerData.node_id == node_id).group_by(PingerData.node_id).all()
    # pprint(last_down_time)
    mean_delay = db.session.query(PingerData.node_id,
                                  (db.func.sum(PingerData.delay) / db.func.count(PingerData.delay)) * 1000). \
        filter(PingerData.delay != None).filter(PingerData.node_id == node_id). \
        group_by(PingerData.node_id).all()
    # pprint(mean_delay)
    try:
        last_up_time = last_up_time[0][1]
    except IndexError:
        last_up_time = None
    try:
        last_down_time = last_down_time[0][1]
    except IndexError:
        last_down_time = None
    try:
        mean_delay = mean_delay[0][1]
    except IndexError:
        mean_delay = None
    return render_template("node_details.html",
                           node_id=node_id,
                           node_name=node_name,
                           last_up_time=last_up_time,
                           last_down_time=last_down_time,
                           mean_delay=mean_delay,
                           page_loc="nodes - details")


@app.route("/manage_nodes", methods=["GET", "POST"])
def manage_nodes():
    all_nodes = db.session.query(Nodes).order_by(Nodes.id.asc()).all()
    return render_template("manage_nodes.html",
                           all_nodes=all_nodes,
                           page_loc="nodes - manage")


@app.route("/add_node", methods=["GET", "POST"])
def add_node():
    form = AddEditNodeForm()
    if form.validate_on_submit():
        # print form.device_type.data
        # print "All is valid"
        # print form.in_use.data
        to_add = Nodes(name=form.name.data,
                       ip=form.ip.data,
                       interface=form.interface.data,
                       node_type=form.node_type.data if form.node_type.data != "None" else None,
                       in_use=form.in_use.data)
        try:
            db.session.add(to_add)
            db.session.commit()
            flash("Successfully added {0}".format(str(to_add)))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not adding nodes - %s" % str(e.message))
        return redirect("/manage_nodes")
    return render_template("add_edit_node.html",
                           form=form,
                           add_edit="add node",
                           page_loc="node - add")


@app.route("/edit/<node_id>", methods=["GET", "POST"])
def edit_node(node_id):
    try:
        to_edit = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
    except IndexError:
        flash("Edit not successful!")
        return redirect("/manage_nodes")
    form = AddEditNodeForm()
    if form.validate_on_submit():
        print "Edit form Valid"
        to_edit.name = form.name.data
        to_edit.ip = form.ip.data
        to_edit.interface = form.interface.data
        to_edit.node_type = form.node_type.data if form.node_type.data != "None" else None
        to_edit.in_use = form.in_use.data
        try:
            db.session.commit()
            flash("Successfully edited {0}".format(str(to_edit)))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            print e
            flash("Not editing nodes - %s" % str(e.message))
        return redirect("/manage_nodes")

    form.name.data = to_edit.name
    form.ip.data = to_edit.ip
    form.interface.data = to_edit.interface
    form.node_type.data = to_edit.node_type
    form.in_use.data = to_edit.in_use
    form.node_id = to_edit.id
    return render_template("add_edit_node.html",
                           form=form,
                           add_edit="edit node",
                           page_loc="nodes - edit")


@app.route("/toggle_node_in_use/<node_id>", methods=["GET", "POST"])
def toggle_node_in_use(node_id):
    print "Toggle row"
    try:
        to_toggle = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
    except IndexError:
        flash("Toggle not successful!")
        return redirect("/manage_nodes")
    # print to_toggle
    to_toggle.in_use = not to_toggle.in_use
    try:
        db.session.commit()
        # flash("Successfully toggled {0}".format(str(to_toggle)))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print e
        flash("Toggle not successful - %s" % str(e.message))
    return redirect("/manage_nodes")


@app.route("/delete/<node_id>", methods=["GET", "POST"])
def delete_node(node_id):
    print "delete row"
    try:
        to_delete = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
        data_to_delete = db.session.query(PingerData).filter(PingerData.node_id == node_id).all()
    except IndexError:
        flash("Delete not successful!")
        return redirect("/manage_nodes")
    # print to_delete
    try:
        db.session.delete(to_delete)
        for data in data_to_delete:
            db.session.delete(data)
        db.session.commit()
        flash("Successfully deleted {0} and it's data".format(str(to_delete)))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print e
        flash("Delete not successful - %s" % str(e.message))
    return redirect("/manage_nodes")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        print form.plot_back_period.data
        update_setting("details_plot_back_period",
                       form.plot_back_period.data,
                       int)
        flash("Settings successfully changed!")
    back_period, _ = get_setting("details_plot_back_period", int)
    form.plot_back_period.data = back_period
    return render_template("settings.html",
                           form=form,
                           page_loc="nodes - settings")


@app.route("/agregator")
def view_agregator():
    return render_template("agregator.html",
                           page_loc="agregator")

@app.route('/temp', methods=["GET", "POST"])
def test():
    to_delete = db.session.query(PingerData).filter(PingerData.node_id == 2).all()
    # print to_delete
    for data in to_delete:
        db.session.delete(data)
    db.session.commit()
    return render_template("view_nodes.html")


# ###################################################
#                                                   #
#                  API VIEWS                        #
#                                                   #
# ###################################################


@app.route("/api/delay_data/<node_id>")
def get_node_delay_data(node_id=None):
    back_period, _ = get_setting("details_plot_back_period", int)
    data = db.session.query(PingerData.date_time, PingerData.delay, Nodes.name).join(Nodes). \
        filter(Nodes.id == PingerData.node_id).filter(Nodes.id == node_id). \
        order_by(PingerData.date_time.desc()).limit(back_period).all()
    node_data = []
    up_times = []
    down_data = []
    for delay in data:
        node_data.append(delay[1] * 1000 if delay[1] is not None else None)
        up_times.append(time_since_epoch(delay[0])*1000)
        down_data.append(-0.01 if delay[1] is None else None)
    # pprint(node_data)
    # pprint(down_data)
    # pprint(up_times)
    series = {"data": [
        {
            "name": "Node Up",
            "data": zip(up_times, node_data),
            "color": "green"
        },
        {
            "name": "Node Down",
            "data": zip(up_times, down_data),
            "color": "red"
        }
    ],
        "back_period": back_period}
    # pprint(series)
    return jsonify(**series)


# ###################################################
#                                                   #
#                  HELPER FUNCTIONS                 #
#                                                   #
# ###################################################

def delete_node_data(node_id):
    data_to_delete = db.session.query(PingerData).filter(PingerData.node_id == node_id).all()
    # print data_to_delete
    for data in data_to_delete:
        db.session.delete(data)
    db.session.commit()


def find_in_lists(data, search, index):
    for d in data:
        if d[index] == search:
            return d
    return None


def get_setting(setting_name, ret_type):
    value = ret_type(db.session.query(AppSettings.value).filter(AppSettings.name == setting_name).first()[0])
    default = ret_type(db.session.query(AppSettings.default_value).filter(AppSettings.name == setting_name).first()[0])
    return value, default


def update_setting(setting_name, new_value, ret_type):
    to_update = db.session.query(AppSettings).filter(AppSettings.name == setting_name).first()
    to_update.value = ret_type(new_value)
    db.session.commit()


def time_since_epoch(t):
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()
