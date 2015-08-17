__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import sqlalchemy
import datetime

from app.common.net import is_up
from app import db
from app.models import Nodes, LastEntry, PingerData


def ping_all():
    devices = db.session.query(Nodes.id, Nodes.name, Nodes.ip).\
        filter(Nodes.in_use != False).all()
    common_id = db.session.query(LastEntry.last_common_id).\
        order_by(LastEntry.date_time.desc()).first()[0] + 1
    for device in devices:
        print device.ip
        up, delay = is_up(device.ip, timeout=0.9)
        data = PingerData(date_time=datetime.datetime.today(),
                          common_id=common_id,
                          up=up,
                          node_id=device.id,
                          delay=delay)
        try:
            db.session.add(data)
            db.session.commit()
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.OperationalError) as e:
            print "Can't add data"
            print e
    increment_last = LastEntry(datetime.datetime.today(), common_id)
    try:
            db.session.add(increment_last)
            db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print "Can't add data"
        print e


def scan():
    for ip in ["192.168.1.{0}".format(last) for last in range(256)]:
        if is_up(ip, timeout=0.5)[0]:
            print "{0} is up!".format(ip)
        # else:
        #     print ip, "is down!"


if __name__ == '__main__':
    ping_all()
    # scan()

    # import sched, time
    # import threading
    #
    # def pinger_worker():
    #     print "Pinger Worker"
    #     s = sched.scheduler(time.time, time.sleep)
    #
    #     def do_something(sc):
    #         print "Doing stuff..."
    #         ping_all()
    #         sc.enter(30, 1, do_something, (sc,))
    #
    #     s.enter(30, 1, do_something, (s,))
    #     s.run()
    #
    # t = threading.Thread(target=pinger_worker)
    # t.daemon = True
    # t.start()
    # t.join()
