import os.path
import sys
import math

# RRD module
import rrdtool

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

# Update existing rrd database
# Main function
def commit():
    # RRD databases list
    rrd = {'mem' : 'Memory.rrd', 'net' : 'Network.rrd', 'cpu' : 'Cpu.rrd'}
    for key, value in rrd.iteritems():
        db_check = check_db(value)
        if db_check == True:
            update_db(rrd, key)
            graph(rrd, key)
            # Create graph
        else:
            print('DB '+value+'created')
            new_db(rrd, key)

# Check of rrd db file
def check_db(db):
    rrd_db = db_path + db
    return os.path.isfile(rrd_db)

# Update DB functions
#####################

# Get traffic value
def get_traf(cmd):
    import os
    out = os.popen(cmd).read()
    print out.strip()
    out = int(out.strip())/1024/1024
    return out

# Update rrd database
def update_db(rrd, db_type):
    rrd_db = db_path + rrd[db_type]
    # Update network DB
    if db_type == 'net':
        in_cmd = 'ifconfig eth0 | grep bytes | grep RX | cut -d":" -f3 | cut -d" " -f1'
        in_traf = get_traf(in_cmd)
        out_cmd = 'ifconfig eth0 | grep bytes | grep TX | cut -d":" -f3 | cut -d" " -f1'
        out_traf = get_traf(out_cmd)
        print('Updating DB')
        # Update rrd db
        ret = rrdtool.update(rrd_db, 'N:%s:%s' %(in_traf, out_traf))

# End of update DB functions
############################

# Create graph functions
########################

def graph(rrd, db_type):
    png = png_path + db_type + '.png'
    db = db_path + rrd[db_type]
    if db_type == 'net':
        rrdtool.graph(png, '--start', 'end-120000s', '--width', '400',
            "--vertical-label=Num", "-M",
            '--watermark=OpenSAN2', '-w 800',
            "DEF:in="+ db +":in:AVERAGE",
            "DEF:out="+ db +":out:AVERAGE",
            "LINE1:in#0000FF:in\\r",
            "LINE2:out#00FF00:out\\r",
            "GPRINT:in:AVERAGE:Avg in\: %6.0lf ",
            "GPRINT:out:MAX:Max in\: %6.0lf \\r",
            "GPRINT:in:AVERAGE:Avg out\: %6.0lf ",
            "GPRINT:out:MAX:Max out\: %6.0lf \\r")
        print('Graph generated')

# End of create graph functions
###############################

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
