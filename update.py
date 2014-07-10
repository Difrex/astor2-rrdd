from rrdsys import get_mem, get_traf, get_cmd, interfaces
from graph import *
# RRD module
import rrdtool

# Update DB functions
#####################

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

# Update rrd database
def update_db(rrd, db_type):
    rrd_db = db_path + rrd[db_type]
    # Update network DB
    if db_type == 'net':
        update_net(rrd)
    elif db_type == 'mem':
        update_mem(rrd, db_type)

# Update memory DB
def update_mem(rrd, db_type):
        rrd_db = db_path + rrd[db_type]
        #Get memmory data
        mem = get_mem()

        print mem # Debug
        # Update rrd db
        print('Updating mem DB')
        rrdtool.update( rrd_db, 'N:%s:%s:%s:%s:%s' % (int(mem['free'])*1000,
            int(mem['total'])*1000, int(mem['buffers'])*1000, int(mem['cached'])*1000, int(mem['used'])*1000 ))

        # Generate graph
        graph(rrd, db_type)
        print('Memory graph generated')

def update_net(rrd):
    traffic = get_traf()
    for i in traffic.iteritems():
        rrd_db = db_path + i[0] + '.' + rrd['net']
        # Update rrd db
        rrdtool.update( rrd_db, 'N:%s:%s' % ( int(i[1]['in']), int(i[1]['out']) ))
        # Generate graph
        graph(rrd, 'net')

# End of update DB functions
############################
