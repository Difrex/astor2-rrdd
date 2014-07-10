from rrdsys import get_mem, get_traf, get_cmd, interfaces
from update import *
from create import new_db, check_db

import os.path
from os.path import join

# RRD module
import rrdtool

# Update existing rrd database
# Main function
def commit():
    # RRD databases list
    rrd = { 'mem': 'Memory.rrd', 'net': 'Network.rrd', 'cpu': 'Cpu.rrd' }
    for key, value in rrd.iteritems():
        if check_db(rrd, key) != True:
            new_db(rrd, key)
            print('DB '+value+' created')
        else:
            update_db(rrd, key)
