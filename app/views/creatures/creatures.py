from flask import render_template, Blueprint, jsonify
from app.models import PingerData, Nodes, LastEntry
from app import db
from app.common.stats import histogram

from sqlalchemy import func
import datetime

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

blueprint = Blueprint('creatures_blueprint', __name__, template_folder='templates')


@blueprint.route('/creatures')
def show_creatures():
    """Render creatures.

    :return: response
    """

    return render_template("creatures.html", page_loc="creatures")


#############
# ##     ## #
#    API    #
# ##     ## #
#############

@blueprint.route("/api/creatures_data")
def get_creatures_data():
    creatures = db.session.query(Nodes.name, Nodes.id).filter(Nodes.id.in_((10, 12))). \
        order_by(Nodes.id.asc()).all()

    # TODO. Update time for every single sensor
    timestamp = db.session.query(LastEntry.date_time).order_by(LastEntry.date_time.desc()).first()[0]
    print timestamp

    creatures_data = []  # Data for all creatures together
    hist_data_day = []
    hist_data_week = []
    for creature in creatures:
        print "\n", creature.name, creature.id
        node_id = creature.id

        all_count = db.session.query(func.count(PingerData.id)).filter(PingerData.node_id == node_id).first()[0]
        down_count = db.session.query(func.count(PingerData.id)).filter(PingerData.node_id == node_id). \
            filter(PingerData.up == False).first()[0]
        up_count = all_count - down_count

        print "all:", all_count
        print "up:", up_count, up_count / (0.01 * all_count), "%"
        print "down:", down_count, down_count / (0.01 * all_count), "%\n"

        creatures_data.append([{"name": "{0}".format(creature.name), "y": up_count, "up": "Up"},
                               {"name": "{0}".format(creature.name), "y": down_count, "up": "Down"}])

        time_up_data = db.session.query(PingerData.date_time).filter(PingerData.node_id == node_id).\
            filter(PingerData.up == True).all()
        hist_data_day.append(histogram([x[0].hour for x in time_up_data], 1, 0, 23))
        hist_data_week.append(histogram([x[0].weekday() for x in time_up_data], 1, 0, 6))

    series = {"creatures_data": creatures_data,
              "hist_data_day": hist_data_day,
              "hist_data_week": hist_data_week,
              "last_update_time": datetime.datetime.strftime(timestamp, "%d.%m.%Y %H:%M:%S")
              }
    return jsonify(**series)
