# coding=utf-8
from flask import render_template
from app import app


from home.home import blueprint as hom_blueprint
from aggregator.aggregator import blueprint as agg_blueprint
from environment.environment import blueprint as env_blueprint
from nodes.nodes import blueprint as nod_blueprint
from server.server import blueprint as ser_blueprint
from settings.settings import blueprint as set_blueprint

app.register_blueprint(blueprint=hom_blueprint)
app.register_blueprint(blueprint=agg_blueprint)
app.register_blueprint(blueprint=env_blueprint)
app.register_blueprint(blueprint=nod_blueprint)
app.register_blueprint(blueprint=ser_blueprint)
app.register_blueprint(blueprint=set_blueprint)

__author__ = 'Lesko'


# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

# basic_auth = BasicAuth(app)


@app.errorhandler(404)
def page_not_found(e):
    """Handles when unknown address is requested.

    :param e: error code description
    :return: response
    """
    return render_template('404.html',
                           page_loc="404"), 404


# def delete_node_data(node_id):
#     data_to_delete = db.session.query(PingerData).filter(PingerData.node_id == node_id).all()
#     # print data_to_delete
#     for data in data_to_delete:
#         db.session.delete(data)
#     db.session.commit()
