from app import app
import sys

argv = sys.argv
if len(argv) != 2:
    print "ERROR! Specify IP address!"
    sys.exit()
ip = argv[1]

app.run(host=ip, port=5000, debug=True, threaded=True)
