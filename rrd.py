import os.path
# RRD module
from rrdtool import *

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
	fname = rrd_db
	rrd = RoundRobinDatabase(fname)
	# Create network database
	rrd.create(
		DataSource("in", type=DeriveDST, heartbeat=600, min=0, max=12500000),
		DataSource("out", type=DeriveDST, heartbeat=600, min=0, max=12500000),
		RoundRobinArchive(cf=AverageCF, xff=0.5, steps=1, rows=576),
		RoundRobinArchive(cf=AverageCF, xff=0.5, steps=6, rows=672),
		RoundRobinArchive(cf=AverageCF, xff=0.5, steps=24, rows=732),
		RoundRobinArchive(cf=AverageCF, xff=0.5, steps=144, rows=1460),
		step=300
		)
	print('Database created')