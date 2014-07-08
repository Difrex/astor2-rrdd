# RRDd
RRD collection and graph generation daemon.

## Create dirrectories

	mkdir -p /var/lib/astor2-rrdd/{rrd,png}
	mkdir -p /var/run/astor2-rrdd/
	mkdir -p /var/log/astor2-rrdd/

## Install modules

	yum install python-daemon
	apt-get install python-daemon

## Usage
	
	./rrdd [start|stop|restart]