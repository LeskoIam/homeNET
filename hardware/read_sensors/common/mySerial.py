import serial
import time

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


class MySerial(object):

    def __init__(self, port, baudrate, prompt, default_timeout=60, debug=False):
        self.port = port
        self.baudrate = baudrate
        self.prompt = prompt
        self.default_timeout = default_timeout
        self.connected = False
        self.serial = None
        self.debug = debug

    def __str__(self):
        return "Serial on port {port}".format(port=self.port)

    def _debug(self, my_str):
        if self.debug:
            print "++dbg:", repr(my_str)

    def connect(self):
        if self.serial is None:
            self.serial = serial.Serial(self.port, baudrate=self.baudrate)
            self.connected = True
        else:
            raise AttributeError("Connection already opened!")

    def close(self):
        if self.connected:
            self.serial.close()
            self.connected = False
            self.serial = None
        else:
            raise AttributeError("Connection already closed!")

    def expect(self, prompt, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        elif type(timeout) not in [int, float]:
            raise TypeError("Timeout must be 'float' or 'integer'")
        if type(prompt) is not str:
            raise TypeError("Prompt must be 'str'")
        start_time = time.time()
        in_string = ""
        while True:
            if time.time() - start_time > timeout:
                return None
            if self.serial.inWaiting() != 0:
                in_data = str(self.serial.read(1))
            else:
                continue
            in_string += in_data
            if in_string[-len(prompt):] == prompt:
                return in_string

    def send(self, command, prompt=None, timeout=10):
        if timeout is None:
            timeout = self.default_timeout
        elif type(timeout) not in [int, float]:
            raise TypeError("Timeout must be 'float' or 'integer'")
        if prompt is None:
            prompt = self.prompt
        elif type(prompt) is not str:
            raise TypeError("Prompt must be 'str'")
        if type(command) is not str:
            raise TypeError("Command must be 'str'")

        self._debug("Sending command: '{comm}'".format(comm=command))
        if self.connected:
            self.serial.write(str(command))
            rcv = self.expect(prompt, timeout)
            self._debug("Received: '{rcv}'".format(rcv=rcv))
            return rcv
        else:
            raise AttributeError("Connection closed!")


if __name__ == '__main__':
    ard = MySerial("/dev/ttyAMA0", baudrate=115200, prompt=">>", debug=True)
    ard.connect()
    commands = ["1", "2", "3", "4"]

    print ard.expect(">>", timeout=1)
    # print ard.send("\r")
 
    for c in commands:
        print "##########################################"
        ans = ard.send(c, timeout=5)
        if ans is None:
            print "None recived"
            continue
        if "NOK" in ans:
            print "NOK"
        else:
            print "OK"
        # time.sleep(3)

    ard.close()
