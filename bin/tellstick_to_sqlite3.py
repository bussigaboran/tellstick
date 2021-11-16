#!/usr/bin/env python

import os.path
import subprocess
import sqlite3

log_path = "/home/boran/sensors/tellstick_net/log/"
dbfile = log_path + "temperature.db"


def td_get_sensor_data(sensor_id):
    device = {}
    device['sensor_id'] = sensor_id
    log_path = "/home/boran/sensors/tellstick_net/log/"
    p = subprocess.Popen(["./tdtool.py", "--sensor-data", str(sensor_id)],
                         stdout = subprocess.PIPE,
                         stderr = subprocess.STDOUT)
    out = p.communicate()[0]
    sensor_data = out.split('\n')
    sensor_data.pop()  # We don't want the last newline turn into an empty list
    for sensor_reading in sensor_data:
        if sensor_reading != None:
            s_name, s_type, reading, timestamp = [splits for splits in sensor_reading.split('\t') if splits is not ""]
            #s_name, s_type, reading, timestamp = sensor_reading.split('\t')
            device['name'] = s_name
            device['timestamp'] = timestamp
            if s_type == "temp":
                device['temperature'] = reading
            if s_type == "humidity":
                device['humidity'] = reading
    return device


def td_list_sensors():
    """ Get list of sensors from tellstick.net """
    sensor_list = []
    p = subprocess.Popen(["./tdtool.py", "--list-sensors"],
                         stdout = subprocess.PIPE,
                         stderr = subprocess.STDOUT)
    out = p.communicate()[0]
    sensors = out.split('\n')
    for sensor in sensors:
        if '-' in sensor:
            if 'undef' not in sensor:
                sensor_id = sensor.split()[0]
                sensor_list.append(sensor_id)
    return sensor_list


def connect_db(fname):
    create_tables = 0
    # A connect call creates a db file if it doesn't exist, therefore
    # we perform the file check beforehand
    if (os.path.isfile(fname) == False):
        create_tables = 1
    db = sqlite3.connect(fname)
    c = db.cursor()
    if create_tables:
        c.execute('''CREATE TABLE sensors(sensor_id text, name text,
                    timestamp text, temperature text, humidity text)''')
    return db, c


def update_db(c, device):
    c.execute('''INSERT INTO sensors(sensor_id, name, timestamp,
                temperature, humidity)
                  VALUES(?,?,?,?,?)''',
                  (device['sensor_id'],
                   device['name'],
                   device['timestamp'],
                   device['temperature'],
                   device['humidity']))


def main():
    sensor_list = td_list_sensors()
    # sensors = sensor_list.split('\n')
    db, c = connect_db(dbfile)
    for sensor_id in sensor_list:
        device = td_get_sensor_data(sensor_id)
        update_db(c, device)
    db.commit()
    db.close()


if __name__ == "__main__":
    main()

