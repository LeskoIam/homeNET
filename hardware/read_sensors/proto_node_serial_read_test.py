from sqlalchemy import create_engine
from common import mySerial
import datetime
import time

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result

    return timed


@timeit
def get_ds_temp(padding=5, mean_n=0):
    command = "1"
    timeout = 5
    for _ in range(padding):
        ard.send(command, timeout=timeout)

    if mean_n:
        rs = []
        for _ in range(mean_n):
            temp = float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])
            rs.append(temp)
        return sum(rs)/len(rs)
    return float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])


@timeit
def get_dht_temp(padding=5, mean_n=0):
    command = "2"
    timeout = 5
    for _ in range(padding):
        ard.send(command, timeout=timeout)

    if mean_n:
        rs = []
        for _ in range(mean_n):
            temp = float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])
            rs.append(temp)
        return sum(rs)/len(rs)
    return float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])


@timeit
def get_dht_hum(padding=5, mean_n=0):
    command = "3"
    timeout = 5
    for _ in range(padding):
        ard.send(command, timeout=timeout)

    if mean_n:
        rs = []
        for _ in range(mean_n):
            hum = float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])
            rs.append(hum)
        return sum(rs)/len(rs)
    return float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])


@timeit
def get_ldr_lig(padding=5, mean_n=0):
    command = "4"
    timeout = 5
    for _ in range(padding):
        ard.send(command, timeout=timeout)

    if mean_n:
        rs = []
        for _ in range(mean_n):
            hum = float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])
            rs.append(hum)
        return sum(rs)/len(rs)
    return float(ard.send(command, timeout=timeout).split("\n")[-3].split(" ")[-1])


def main():
    print
    ds_temp = get_ds_temp(5, 5)
    print ds_temp
    ds_temp = get_ds_temp(5, 0)
    print ds_temp

    print
    dht_temp = get_dht_temp(5, 5)
    print dht_temp
    dht_temp = get_dht_temp(5, 0)
    print dht_temp

    print
    dht_hum = get_dht_hum(5, 5)
    print dht_hum
    dht_hum = get_dht_hum(5, 0)
    print dht_hum

    print
    ldr_lig = get_ldr_lig(5, 5)
    print ldr_lig
    ldr_lig = get_ldr_lig(5, 0)
    print ldr_lig


def main_to_db():
    eng = create_engine('postgresql://lesko:ma19ne99@192.168.1.53/homeNET')
    with eng.connect() as con:
        d = con.execute("SELECT value FROM app_settings WHERE name = 'TEMPERATURE_SCAN_PERIOD';")

        sleep_time = d.first()
        sleep_time = float(sleep_time[0])

    timestamp = datetime.datetime.today()
    ts = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    ds_temp = get_ds_temp(5, 5)
    print "{0}\t{1} degC".format(ts, ds_temp)

    dht_temp = get_dht_temp(5, 5)
    print "{0}\t{1} degC".format(ts, dht_temp)

    dht_hum = get_dht_hum(5, 5)
    print "{0}\t{1} %".format(ts, dht_hum)

    ldr_lig = get_ldr_lig(5, 5)
    print "{0}\t{1} e".format(ts, ldr_lig)

    with eng.connect() as con:
        rs = con.execute("INSERT INTO sensor_data (sensor_id, date_time, value, unit) VALUES (%s,%s,%s,%s)",
                         (12, timestamp, ds_temp, "C"))
        rs = con.execute("INSERT INTO sensor_data (sensor_id, date_time, value, unit) VALUES (%s,%s,%s,%s)",
                         (13, timestamp, dht_temp, "C"))
        rs = con.execute("INSERT INTO sensor_data (sensor_id, date_time, value, unit) VALUES (%s,%s,%s,%s)",
                         (14, timestamp, dht_hum, "%"))
        rs = con.execute("INSERT INTO sensor_data (sensor_id, date_time, value, unit) VALUES (%s,%s,%s,%s)",
                         (15, timestamp, ldr_lig, "e"))
    print "Sleeping for {0}s".format(sleep_time)
    time.sleep(sleep_time)


if __name__ == '__main__':
    ard = mySerial.MySerial("/dev/ttyAMA0", baudrate=115200, prompt=">>", debug=False)
    ard.connect()

    print ard.expect(">>", timeout=1)

    while "pigs" != "fly":
        main_to_db()
        # break

    ard.close()
