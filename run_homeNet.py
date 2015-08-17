from app import app
import sys
# import sched, time
# import threading
# from app.pinger.pinger import ping_all

argv = sys.argv
if len(argv) != 2:
    print "ERROR! Specify IP address!"
    sys.exit()
ip = argv[1]


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

app.run(host=ip, port=5000, debug=True)
# t.join()
