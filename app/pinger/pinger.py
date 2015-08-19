__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.
import datetime
import socket
import sqlite3 as lite

import sys
sys.path.append("../..")
from app.common.net import is_up


def ping_all(connection):
    _ip = 2
    _id = 0
    with connection:
        curr = connection.cursor()
        curr.execute("SELECT nodes.id AS nodes_id, nodes.name AS nodes_name, nodes.ip AS nodes_ip FROM nodes WHERE nodes.in_use != 0")
        devices = curr.fetchall()
    with connection:
        curr = connection.cursor()
        common_id = curr.execute("SELECT last_entry.last_common_id AS last_entry_last_common_id FROM last_entry ORDER BY last_entry.date_time DESC LIMIT 1").fetchone()[0] + 1
    with connection:
        curr = connection.cursor()
        curr.execute("INSERT INTO last_entry (date_time, last_common_id, ready_to_read) VALUES (?, ?, ?)",
                     (datetime.datetime.today(), common_id, 0))
        print common_id
    for device in devices:
        print "Pinging:", device[_ip]
        try:
            up, delay = is_up(device[_ip], timeout=0.9)
        except socket.gaierror:
            up, delay = False, None
        with connection:
            curr = connection.cursor()
            curr.execute("INSERT INTO pinger_data (date_time, common_id, up, node_id, delay) VALUES (?,?,?,?,?)",
                         (datetime.datetime.today(), common_id, up, device[_id], delay))
    with connection:
        curr = connection.cursor()
        curr.execute("UPDATE last_entry SET ready_to_read=? WHERE last_common_id=?", (1, common_id))


def scan():
    for ip in ["192.168.1.{0}".format(last) for last in range(256)]:
        if is_up(ip, timeout=0.5)[0]:
            print "{0} is up!".format(ip)
            # else:
            #     print ip, "is down!"


if __name__ == '__main__':
    import time


    def pinger_worker():
        con = lite.connect("D:/workspace/homeNet/app.db")
        while 1:
            start_time = time.time()
            ping_all(con)
            delay = 60
            diff = time.time() - start_time
            if diff < 30:
                delay = 30
            print "Pinger running after:", delay, time.time()
            time.sleep(delay)


    pinger_worker()
#
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
