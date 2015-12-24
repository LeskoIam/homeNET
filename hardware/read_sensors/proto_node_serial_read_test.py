from common import mySerial

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


ard = mySerial.MySerial("/dev/ttyAMA0", baudrate=115200, prompt=">>", debug=True)
ard.connect()
commands = ["1", "2", "3", "4"]

print ard.expect(">>", timeout=1)

for c in commands:
    print "##########################################"
    ans = ard.send(c, timeout=5)
    if ans is None:
        continue
    if "NOK" in ans:
        print "NOK"
    else:
        print "OK"

ard.close()
