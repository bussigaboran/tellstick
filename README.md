# Temperature monitoring using Tellstick

## Preparation
According to the documentation[1], you need the Python OAuth and ConfigObj modules installed for this to work, and also add a keypair for PUBLIC_KEY and PRIVATE_KEY in the tdtool.py script below. You can generate one here: http://api.telldus.com/keys/index [1]

When you have completed the steps above, update the supplied tdtool.py. The page I found it on is unfortunately gone[2] so send the anonymous authors good thoughts and use the supplied version. If you use a version of tdtool.py for another source, make sure it's patched to read sensors. Not all tdtool.py programs are created equal! Update the the script with your keys and you are good to go.

Dead links referred above:

[1] https://developer.telldus.com/blog/new-python-example-for-telldus-live

[2] http://developer.telldus.se/attachment/ticket/114/tdtool-with-sensors.py

## Scripts
The main scripts in this repository are:
- tdtool.py
- plot_tellstick_data.py
- tellstick_to_sqlite3.py

### tdtool.py
Update the script with your keys from above and then use it in the following manner:
```
user@borken.se:~/sensors/tellstick_net/bin> ./tdtool.py --list-sensors
Number of sensors: 6
1537353844      None    2021-11-16 19:51:33
1537353499      0_terrace       2021-11-16 19:59:12
1537354449      0_garage        2021-11-16 19:59:02
1537353504      1_modembox      2021-11-16 20:00:38
1537353509      2_guest_room    2021-11-16 20:01:34
1537353514      2_living_room   2021-11-16 19:52:52

user@borken.se:~/sensors/tellstick_net/bin> ./tdtool.py --sensor-data 1537353499
1_terrace       temp    9.6     2021-11-16 19:59:12
1_terrace       humidity        70      2021-11-16 19:59:12
```
Use "tdtool.py --help" for more options.

### tellstick_to_sqlite3.py
This script uses tdtool.py to retrieve temperature and humidity data from the sensors and store the readings in an sqlite3 database. I like a lot of measurements so I run it from crontab every 5 minutes:
```
*/5 * * * * /home/user/cron/5_minute_jobs.sh
```
Since I have other jobs that run every five minutes, I added all to an sh wrapper that executes them sequentially.

### plot_tellstick_data.py
This script read from the database and generates different matplotlib plots depending on the prefix in the sensor name:
- 0_ - outside the house
- 1_ - first floor
- 2_ - second floor

This script is called from cron every 15 minues as below
```
7,17,37,47 * * * * /home/boran/cron/plot_tellstick_data.py
```
