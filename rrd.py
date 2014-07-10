from rrdsys import get_mem, get_traf, get_cmd, interfaces
import os.path
from os.path import join

# RRD module
import rrdtool

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

# Update existing rrd database
# Main function
def commit():
    # RRD databases list
    rrd = { 'mem': 'Memory.rrd', 'net': 'Network.rrd', 'cpu': 'Cpu.rrd' }
    for key, value in rrd.iteritems():
        db_check = check_db(rrd, key)
        if db_check == True:
            update_db(rrd, key)
        else:
            print('DB '+value+' created')
            new_db(rrd, key)

# Check of rrd db file
def check_db(rrd, db_type):
    if db_type == 'net':
        ifaces = interfaces()
        for i in ifaces:
            rrd_db = db_path + i + '.' + rrd[db_type]
            if os.path.isfile(rrd_db) != True:
                new_db(rrd, db_type)
            else:
                return True
    else:
        rrd_db = db_path + rrd[db_type]
        return os.path.isfile(rrd_db)


# Update DB functions
#####################

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

# Create graph functions
########################

# Switches for graphics
def graph(rrd, db_type):
    if db_type == 'net':
        graph_net(rrd)
        print('Net graphs generated')
    elif db_type == 'mem':
        graph_mem(rrd, db_type)

# Generate graphic for memory usage
def graph_mem(rrd, db_type):
    png = png_path + rrd[db_type] + '.png'
    db = db_path + rrd[db_type]
    rrdtool.graph(png, '--start', '-8192', '--width', '300', '-h', '150',
            "--vertical-label=Gb", 
            '--watermark=OpenSAN2', '-r',
            '--dynamic-labels',
            '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:total="+ db +":total:AVERAGE",
            "DEF:free="+ db +":free:AVERAGE",
            "DEF:used="+ db +":used:AVERAGE",
            "AREA:total#000000:Total memory",
            "AREA:used#aa0000:Used memory",
            "AREA:free#00FF00:Free memory" )


# Generate graphic for network interfaces
def graph_net(rrd):
    ifaces = interfaces()
    for i in ifaces:
        png = png_path + i + '.' + rrd['net'] + '.png'
        db = db_path + i + '.' + rrd['net']
        rrdtool.graph(png, '--start', 'end-6h',
            '--title', 'Network interface ' + i, '-h', '150',
            '--width', '400', "--vertical-label=bits/s",
            '--slope-mode', '-m', '1', '--dynamic-labels',
            '--watermark=OpenSAN2', 
            '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:in="+ db +":in:AVERAGE",
            "DEF:out="+ db +":out:AVERAGE",
            "AREA:out#FF0000:out:STACK",
            "AREA:in#0000FF:in:STACK",
            )

# End of create graph functions
###############################

# rrdtool create functions
# Needs to rewrite
##########################

# Create new db
def new_db(rrd, db_type):
    rrd_db = db_path + rrd[db_type]
    if db_type == 'net':
        create_net(rrd)
    elif db_type == 'mem':
        create_mem(rrd_db)
    elif db_type == 'cpu':
        create_cpu(rrd)

# Create new network DB
def create_net(rrd):
    ifaces = interfaces()
    for i in ifaces:
        rrd_db = db_path + i + '.' + rrd['net']
        data_sources=[ 'DS:in:COUNTER:120:0:U',
                    'DS:out:COUNTER:120:0:U'
                    ]
        # Create network database
        rrdtool.create( rrd_db,
                     '--start', '920804400',
                     data_sources,
                     'RRA:AVERAGE:0.5:1:360',
                     'RRA:AVERAGE:0.5:10:1008',
                     'RRA:AVERAGE:0.5:10:1008',
                    )

# Create new memory DB
def create_mem(rrd_db):
    data_sources = [ 'DS:free:GAUGE:120:0:U',
                'DS:total:GAUGE:120:0:U',
                'DS:cached:GAUGE:120:0:U',
                'DS:buffers:GAUGE:120:0:U',
                'DS:used:GAUGE:120:0:U'
                ]
    # Create network database
    rrdtool.create( rrd_db,
                 data_sources,
                 'RRA:AVERAGE:0.5:1:360',
                 'RRA:AVERAGE:0.5:10:1008,',
                 'RRA:MAX:0.5:10:1008'
                  )

# Create new CPU DB
def create_cpu():
    physicals = cpus()
    cores = cpu_cores()

    if physicals <= 1:
        count = 0
        while count < cores:
            db = '/tmp/' + count + 'cpu.rrd'
            data_sources=[ 'DS:speed1:COUNTER:600:U:U',
                        'DS:speed2:COUNTER:600:U:U',
                        'DS:speed3:COUNTER:600:U:U' ]
            # Create network database
            rrdtool.create( db,
                         '--start', '920804400',
                         data_sources,
                         'RRA:AVERAGE:0.5:1:24',
                         'RRA:AVERAGE:0.5:6:10' )
            count = count + 1

# End of rrdtool create functions
#################################
