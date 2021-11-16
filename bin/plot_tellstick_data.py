#!/usr/bin/env python3

from datetime import datetime, timedelta
import matplotlib
import os.path
import sqlite3
import time
# Use the agg backend before importing pyplot to work around the issue
# with pyplot needing X11
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter


def connect_to_database(fname):
    """ connect to sqlite3 database with tellstick sensor readings """
    if os.path.isfile(fname) is not False:
        database = sqlite3.connect(fname)
        database.text_factory = str
        return database.cursor()


def db_list_sensors(cursor):
    """ Get list of temperature and humidity sensors from database """
    sql = "SELECT DISTINCT name FROM sensors"
    cursor.execute(sql)
    sensor_list = cursor.fetchall()
    # Convert list of lists from database to list:
    # [(u'sensor_1',), (u'sensor_2',)] -> [u'sensor_1', u'sensor_2']
    sensors = [sensors[0] for sensors in sensor_list]
    return sensors


def db_get_2days_temperature_data(cursor, sensor):
    """ Retrieve the last 2 days worth of temperature data """
    timestamp = str(datetime.now() - timedelta(days=2))
    yyday = timestamp.split('.')[0]
    sql = 'SELECT timestamp, temperature FROM sensors WHERE name="%s"' % sensor
    sql2 = sql + ' AND timestamp >= "%s"' % yyday
    cursor.execute(sql2)
    return cursor.fetchall()


def clean_up_list(sensor_list):
    """ Remove 'bad' database entries """
    cleaned_list = []
    for sensor in sensor_list:
        if sensor in ['None', 'undef', '_old']:
            pass
        else:
            cleaned_list.append(sensor)
    return sensor_list


def plot_all_temperatures(cursor, sensor_list):
    """ Split sensors on groups and send data on to graph generation """
    outdoors = []
    first_floor = []
    second_floor = []
    # Split different sensors into the different temperature zones in the house
    for sensor in sensor_list:
        if sensor.startswith('0_'):
            outdoors.append(sensor)
        elif sensor.startswith('1_'):
            first_floor.append(sensor)
        elif sensor.startswith('2_'):
            second_floor.append(sensor)
    if len(outdoors):
        plot_group(cursor, outdoors, "outdoors.png")
    if len(first_floor):
        plot_group(cursor, first_floor, "first_floor.png")
    if len(second_floor):
        plot_group(cursor, second_floor, "second_floor.png")


def plot_group(cursor, sensor_list, filename):
    """ Plot graphs using matplotlib"""
    fig = plt.figure(num=None, figsize=(6.25, 4.6875), dpi=80)
    graph = fig.add_subplot(111)
    graph.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
    fig.suptitle("Temperature: last two days")
    fig.autofmt_xdate()
    for sensor in sensor_list:
            readings = db_get_2days_temperature_data(cursor, sensor)
            y1 = [value for (timestamp, value) in readings]
            y1 = [None if value is '' else float(value) for value in y1]
            x0 = [timestamp for (timestamp, value) in readings]
            x1 = matplotlib.dates.datestr2num(x0)
            graph.plot_date(x=x1, y=y1, fmt="-", label=sensor)
    plt.legend(sensor_list, loc='lower left', prop={"size": 10})
    plt.ylabel("°C")
    plt.grid()
    fname = "/usr/share/nginx/html/graphs/%s" % filename
    plt.savefig(fname)


def main():
    start_time = time.time()
    """ Get tellstick temperature readings from sqlite database 
        and plot a graph using matplotlib """
    dbfile = '/home/boran/sensors/tellstick_net/log/temperature.db'
    cursor = connect_to_database(dbfile)
    sensor_list = db_list_sensors(cursor)
    sensor_list = clean_up_list(sensor_list)
    print("--- clean_up_list %s seconds ---" % (time.time() - start_time))
    plot_all_temperatures(cursor, sensor_list)
    print("--- plot_all_temperatures %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
