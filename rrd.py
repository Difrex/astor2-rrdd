def commit():
	print('test')
	# RRD databases list
	rrd = {'memory' : 'Memory.rrd', 'net' : 'Network.rrd', 'cpu' : 'Cpu.rrd'}
	for key in rrd.iteritems():
		db_check = check_db(rrd[key])
		if db_check == 0:
			# Code to update

def check_db(db):
	db_path = '/var/lib/astor2-rrdd/'
	rrd_db = db_path . db