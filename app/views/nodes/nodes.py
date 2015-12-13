from flask import render_template, Blueprint, flash, redirect, jsonify
from app.models import LastEntry, Nodes, PingerData
from app.forms import AddEditNodeForm
from ..common import get_setting, time_since_epoch
from app import db
import sqlalchemy

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('nodes_blueprint', __name__, template_folder='templates')


@blueprint.route('/view_nodes', methods=["GET", "POST"])
def view_nodes():
    """Show network nodes and their status.

    :return: response
    """
    # LastEntry.ready_to_read == True, to ensure no partial pinger data is displayed.
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


@blueprint.route("/node_details/<node_id>", methods=["GET", "POST"])
def show_node_details(node_id=None):
    """Show node details page filed with specific (node_id) information.

    :param node_id: id of the node
    :return: response
    """
    node_name = db.session.query(Nodes.name).filter(Nodes.id == node_id).first()[0]

    last_up_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == "TRUE").filter(PingerData.node_id == node_id). \
        order_by(PingerData.date_time.desc()).first()
    # pprint(last_up_time)

    last_down_time = db.session.query(PingerData.node_id, PingerData.date_time). \
        filter(PingerData.up == "FALSE").filter(PingerData.node_id == node_id). \
        order_by(PingerData.date_time.desc()).first()
    # pprint(last_down_time)

    # Calculate mean with SQL
    mean_delay = db.session.query(PingerData.node_id,
                                  (db.func.sum(PingerData.delay) / db.func.count(PingerData.delay)) * 1000). \
        filter(PingerData.delay != None).filter(PingerData.node_id == node_id). \
        group_by(PingerData.node_id).all()
    # pprint(mean_delay)

    try:
        last_up_time = last_up_time[1]
    except (IndexError, TypeError):
        last_up_time = None

    try:
        last_down_time = last_down_time[1]
    except (IndexError, TypeError):
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


@blueprint.route("/manage_nodes", methods=["GET", "POST"])
def manage_nodes():
    """Show manage mode view. Nodes can be deleted, added,
     edited in this view.

    :return: response
    """
    all_nodes = db.session.query(Nodes).order_by(Nodes.id.asc()).all()
    return render_template("manage_nodes.html",
                           all_nodes=all_nodes,
                           page_loc="nodes - manage")


@blueprint.route("/add_node", methods=["GET", "POST"])
def add_node():
    """Add node dialog.

    :return: response
    """
    form = AddEditNodeForm()
    if form.validate_on_submit():
        # print form.device_type.data
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


@blueprint.route("/edit/<node_id>", methods=["GET", "POST"])
def edit_node(node_id):
    """Node information can be edited in this view.

    :param node_id: id of the node to be edited
    :return: response
    """
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


@blueprint.route("/toggle_node_in_use/<node_id>", methods=["GET", "POST"])
def toggle_node_in_use(node_id):
    """Toggles visible nodes.

    :param node_id: id of the node to be toggled
    :return: redirect
    """
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


@blueprint.route("/delete/<node_id>", methods=["GET", "POST"])
def delete_node(node_id):
    print "delete row"
    try:
        to_delete = db.session.query(Nodes).filter(Nodes.id == int(node_id)).first()
        # Delete all data associated with this node
        # data_to_delete = db.session.query(PingerData).filter(PingerData.node_id == node_id).all()
    except IndexError:
        flash("Delete not successful!")
        return redirect("/manage_nodes")
    # print to_delete
    try:
        db.session.delete(to_delete)
        # Delete all data associated with this node
        # for data in data_to_delete:
        #     db.session.delete(data)
        db.session.commit()
        flash("Successfully deleted {0} and it's data".format(str(to_delete)))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print e
        flash("Delete not successful - %s" % str(e.message))
    return redirect("/manage_nodes")


#############
# ##     ## #
#    API    #
# ##     ## #
#############

@blueprint.route("/api/delay_data/<node_id>")
def get_node_delay_data(node_id=None):
    back_period = get_setting("NODE_DETAILS_PLOT_BACK_PERIOD", int)
    data = db.session.query(PingerData.date_time, PingerData.delay, Nodes.name).join(Nodes). \
        filter(Nodes.id == PingerData.node_id).filter(Nodes.id == node_id). \
        order_by(PingerData.date_time.desc()).limit(back_period.value).all()
    node_data = []
    up_times = []
    down_data = []
    for delay in data:
        node_data.append(delay[1] * 1000 if delay[1] is not None else None)
        up_times.append(time_since_epoch(delay[0]) * 1000)
        down_data.append(-0.01 if delay[1] is None else None)
    # pprint(node_data)
    # pprint(down_data)
    # pprint(up_times)
    series = {"data": [
        {
            "name": "Node Up",
            "data": zip(up_times, node_data)[::-1],
            "color": "green"
        },
        {
            "name": "Node Down",
            "data": zip(up_times, down_data)[::-1],
            "color": "red"
        }
    ],
        "back_period": back_period.value
    }
    # pprint(series)
    return jsonify(**series)
