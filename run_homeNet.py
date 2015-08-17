from app import app
import sys
# import threading
# from app.pinger.pinger import ping_all
# import time

argv = sys.argv
if len(argv) != 2:
    print "ERROR! Specify IP address!"
    sys.exit()
ip = argv[1]


# def pinger_worker():
#     while 1:
#         start_time = time.time()
#         ping_all()
#         delay = 60
#         diff = time.time() - start_time
#         if diff < 30:
#             delay = 30
#         print "Pinger running after:", delay, time.time()
#         time.sleep(delay)
#
# t = threading.Thread(target=pinger_worker)
# t.daemon = True
# t.start()

app.run(host=ip, port=5000, debug=True)
# t.join()
