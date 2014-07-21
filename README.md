# RRDd

RRD collection and graph generation daemon.

## Create dirrectories

	mkdir -p /var/lib/astor2-rrdd/{rrd,png}
	mkdir -p /var/run/astor2-rrdd/
	mkdir -p /var/log/astor2-rrdd/

## Install requirements

	yum install python-daemon sysstat rrdtool-python
	apt-get install python-daemon sysstat python-rrdtool

## Usage
	
	./rrdd [start|stop|restart]

## License

The BSD 3-Clause License. 
You can find full text in COPYING file.
