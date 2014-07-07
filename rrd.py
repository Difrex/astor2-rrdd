import os.path
import sys

# RRD module
import rrdtool

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

# Update existing rrd databse
def commit():
	# RRD databases list
	rrd = {'mem' : 'Memory.rrd', 'net' : 'Network.rrd', 'cpu' : 'Cpu.rrd'}
	for key, value in rrd.iteritems():
		db_check = check_db(value)
		if db_check == True:
			# Code to update
			return('Database updated')
		else:
			new_db(rrd, key)
			print('Database created')
			# Code to create new db and write to it

# Check of rrd db file
def check_db(db):
	rrd_db = db_path + db
	return os.path.isfile(rrd_db)

# rrdtool create functions
# Needs to rewrite
##########################

# Create new db
def new_db(rrd, db_type):
	rrd_db = db_path + rrd[db_type]
	if db_type == 'net':
		create_net(rrd_db)
	elif db_type == 'mem':
		create_mem(rrd_db)
	elif db_type == 'cpu':
		create_cpu(rrd_db)

# Create new network DB
def create_net(rrd_db):
	data_sources=[ 'DS:in:DERIVE:600:0:12500000',
                'DS:out:DERIVE:600:0:12500000'
                ]
	# Create network database
	rrdtool.create( rrd_db,
                 '--start', '920804400',
                 data_sources,
                 'RRA:AVERAGE:0.5:1:576',
                 'RRA:AVERAGE:0.5:6:672',
                 'RRA:AVERAGE:0.5:24:732',
                 'RRA:AVERAGE:0.5:144:1460'
                )

# Create new memory DB
def create_mem(rrd_db):
	data_sources=[ 'DS:speed1:COUNTER:600:U:U',
                'DS:speed2:COUNTER:600:U:U',
                'DS:speed3:COUNTER:600:U:U' ]
	# Create network database
	rrdtool.create( rrd_db,
                 '--start', '920804400',
                 data_sources,
                 'RRA:AVERAGE:0.5:1:24',
                 'RRA:AVERAGE:0.5:6:10' )

# Create new CPU DB
def create_cpu(rrd_db):
	data_sources=[ 'DS:speed1:COUNTER:600:U:U',
                'DS:speed2:COUNTER:600:U:U',
                'DS:speed3:COUNTER:600:U:U' ]
	# Create network database
	rrdtool.create( rrd_db,
                 '--start', '920804400',
                 data_sources,
                 'RRA:AVERAGE:0.5:1:24',
                 'RRA:AVERAGE:0.5:6:10' )

# End of rrdtool create functions
#################################