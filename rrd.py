from rrdsys import get_mem, get_traf, get_cmd, interfaces
from update import *
from create import new_db, check_db
import config

# RRD module
import rrdtool

# Update existing rrd database
# Main function
def commit():

    rrd={}
    # Generate RRD databases list
    if config.MEM_ENABLED:
        rrd['mem']='Memory.rrd'
    if config.CPU_ENABLED:
        rrd['cpu']='Cpu.rrd'
    if config.NET_ENABLED:
        rrd['net']='Network.rrd'
    if config.BATTERY_ENABLED:
        rrd['bat']='Battery.rrd'
    print(rrd)

    for key, value in rrd.iteritems():
        if check_db(rrd, key) != True:
            new_db(rrd, key)
            print('DB '+value+' created')
        else:
            update_db(rrd, key)
