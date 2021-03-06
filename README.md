# homeNET
Always wanted to have a local network (intranet) landing site.
This is what I came up with. It's a project in it's infancy and will be added on as I remember new stuff.

In last months this project took a turn, turn into hardware waters. I'm expanding it to include sensorics to monitor
home temperature, humidity, light level,... I'm planning on implementing "smart house" like automation too.
For this I'm developing sensorics and control hardware nodes and  main "processing" unit. For now everything is
implemented with open hardware (RPi, Arduino), but will be integrated if there is need in the future (production?).

The idea is to have a single place where relevant information (relevant to me/you) can be quickly accessed.
I run a small-ish home network with a server, NAS, a few [BBB](http://beagleboard.org/black), oscilloscope
with IP "GPIB" plus a few virtual machines and it's nice to know if devices are up and running just by
looking at this page.

I also wanted to know how my server is doing, is it overheating and what's the processor load. All this
information is available on the Server page.

Feel free to clone, suggest, and so on.

With this project I wanted to learn about web design because I don't have many experiences in this
field. So I'm using new to me things (highcharts, bootstrap, jquery).

Project uses this software "stack":

* [postgreSQL](http://www.postgresql.org/) for data storage (It's free and very, very good!)
* [flask](http://flask.pocoo.org/) for backend
* [bootstrap](http://getbootstrap.com/) for frontend
* [highcharts](http://www.highcharts.com/) for plotting
* [jquery](https://jquery.com/)

## Features
Features are constantly added and improved and are therefor constantly changing.

### 1. Nodes view
A node is a local or internet network address (www.google.com, 192.168.1.1).
Every node is periodically pinged to check if it is alive and what its ping delay is.
All information is logged to database for app use.

There is also a detailed node view where additional information and delay plot is available.

### 2. Aggregator
It will serve as a quick information view.
Various information from local network, internet, weather,...

### 3. Server
Local server temperature and load monitoring.
Parses [Core Temp](http://www.alcpu.com/CoreTemp/) logs for data. Shows individual core temperature
and load data.

Historical data is shown in a plot.

