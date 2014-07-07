import os.path

db_path = '/var/lib/astor2-rrdd/'

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
			# Code to create new db and write to it

def check_db(db):
	rrd_db = db_path + db
	return os.path.isfile(rrd_db)

def new_db(db):
	rrd_db = db_path + db
