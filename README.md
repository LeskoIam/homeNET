# homeNET
Web app for local network home page.
It uses:

* [postgreSQL](http://www.postgresql.org/) for data storage.
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

There is also a detailed node view where additional information about the node is available.

### 2. Aggregator
Various information from local network, internet, weather,...

### 3. Server
Local server temperature and load monitoring. 
Parses [Core Temp](http://www.alcpu.com/CoreTemp/) logs for data. Shows individual core temperature 
and load data.

Historical data is shown a plot.

