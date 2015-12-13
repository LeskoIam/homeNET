from sqlalchemy import create_engine
import time
import datetime
from w1thermsensor import W1ThermSensor

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.

sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000073c6f1f")
eng = create_engine('postgresql://lesko:ma19ne99@192.168.1.53/homeNET')

while "pigs" != "fly":
    with eng.connect() as con:
        d = con.execute("SELECT value FROM app_settings WHERE name = 'TEMPERATURE_SCAN_PERIOD';")

        sleep_time = d.first()
        sleep_time = float(sleep_time[0])

    timestamp = datetime.datetime.today()
    ts = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    temp = sensor.get_temperature()
    print "{0}\t{1} degC".format(ts, temp)

    with open("temp_data.txt", "a") as tempf:
        tempf.write("{0}\t{1}\n".format(ts, temp))

    with eng.connect() as con:
        rs = con.execute("INSERT INTO sensor_data (sensor_id, date_time, value, unit) VALUES (%s,%s,%s,%s)",
                         (1, timestamp, temp, "C"))
    time.sleep(sleep_time)
