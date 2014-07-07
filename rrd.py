import os.path
import sys

# RRD module
import rrdtool

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

def commit():
	# RRD databases list
	rrd = {'memory' : 'Memory.rrd', 'net' : 'Network.rrd', 'cpu' : 'Cpu.rrd'}
	for key, value in rrd.iteritems():
		db_check = check_db(value)
		if db_check == True:
			print('Ok')
			# Code to update
		else:
			print('Not ok')
			new_db(rrd, key)
			# Code to create new db and write to it

def check_db(db):
	rrd_db = db_path + db
	return os.path.isfile(rrd_db)

# Create new db
def new_db(rrd, db_type):
	rrd_db = db_path + rrd[db_type]
	if db_type == 'net':
		create_net(rrd_db)

# Create new net DB
def create_net(rrd_db):
	data_sources=[ 'DS:speed1:COUNTER:600:U:U',
                'DS:speed2:COUNTER:600:U:U',
                'DS:speed3:COUNTER:600:U:U' ]
	# Create network database
	rrdtool.create( rrd_db,
                 '--start', '920804400',
                 data_sources,
                 'RRA:AVERAGE:0.5:1:24',
                 'RRA:AVERAGE:0.5:6:10' )
	print('Database created')