from flask import render_template, Blueprint, jsonify
from app.models import LastEntry, Nodes, PingerData
from app import db

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('aggregator_blueprint', __name__, template_folder='templates')


@blueprint.route("/aggregator")
def view_aggregator():  # aggregator
    return render_template("aggregator.html",
                           page_loc="aggregator")


#############
# ##     ## #
#    API    #
# ##     ## #
#############

@blueprint.route("/api/network_summary")
def get_network_summary():
    # Out of M nodes (n_all_nodes) N are active (pinged) and U nodes are up
    n_all_nodes = db.session.query(db.func.count(Nodes.id)).one()[0]
    n_all_active_nodes = db.session.query(db.func.count(Nodes.id)).filter(Nodes.in_use == True).one()[0]
    last_common_id = db.session.query(LastEntry.last_common_id).filter(LastEntry.ready_to_read == True). \
        order_by(LastEntry.date_time.desc()).first()[0]
    n_all_up_nodes = db.session.query(db.func.count(PingerData.id)).filter(Nodes.id == PingerData.node_id). \
        filter(PingerData.common_id == last_common_id). \
        filter(PingerData.up == True).one()[0]

    # print n_all_nodes, type(n_all_nodes)
    # print n_all_active_nodes, type(n_all_active_nodes)
    # print last_common_id
    # print n_all_up_nodes

    data = {
        "network": {
            "n_all_nodes": n_all_nodes,
            "n_all_active_nodes": n_all_active_nodes,
            "n_all_up_nodes": n_all_up_nodes
        }
    }
    return jsonify(data)
