import os.path
from os import listdir
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
            print('DB '+value+'created')
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

# Get network interfaces list
def interfaces():
    sys_path = '/sys/class/net'
    ifaces = [ f for f in listdir(sys_path) if join(sys_path, f) ]
    ifaces.remove('lo')
    return ifaces

# Get traffic values
def get_traf():
    ifaces = interfaces()
    traffic = {}

    # Parsing /proc/net/dev
    proc = '/proc/net/dev'
    f = open(proc, "r")
    for line in f.readlines():
        bytes = line.split()
        for i in ifaces:
            net = bytes[0]
            net = net[:-1]
            if i == net:
                traffic[i] = { 'in': bytes[1], 'out': bytes[9] }
    return traffic

# Get cmd value
def get_cmd(cmd):
    import os
    os.popen(cmd).read()
    return int(os.popen(cmd).read())

# Update rrd database
def update_db(rrd, db_type):
    rrd_db = db_path + rrd[db_type]
    # Update network DB
    if db_type == 'net':
        update_net(rrd)
    elif db_type == 'mem':
        update_mem(rrd, db_type)

def update_mem(rrd, db_type):
        rrd_db = db_path + rrd[db_type]
        #Get memmory data
        memtotal_cmd="grep MemTotal /proc/meminfo | awk '{print $2}'"
        print("Total:")
        memtotal=get_cmd(memtotal_cmd)


        print("Free:")
        memfree_cmd="cat /proc/meminfo | grep MemFree | awk '{print $2}'"
        memfree=get_cmd(memfree_cmd)
        print memfree

        print("Cached:")
        cached_cmd="cat /proc/meminfo | grep -v Swap | grep Cached | awk '{print $2}'"
        cached=get_cmd(cached_cmd)

        print("Buffers:")
        buffers_cmd="cat /proc/meminfo | grep Buffers | awk '{print $2}'"
        buffers=get_cmd(buffers_cmd)

        print("Used:")
        used=memtotal
        print(used)

        # Update rrd db
        print('Updating mem DB')
        rrdtool.update( rrd_db, 'N:%s:%s:%s:%s:%s' % (memfree, memtotal, buffers, cached, used) )
        graph(rrd, db_type)

def update_net(rrd):
    traffic = get_traf()
    for i in traffic.iteritems():
        rrd_db = db_path + i[0] + '.' + rrd['net']
        # Update rrd db
        print "Updating " + rrd_db
        rrdtool.update(rrd_db, 'N:%s:%s' % (i[1]['in'], i[1]['out']))
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
    elif db_type == 'mem':
        graph_mem(rrd, db_type)

# Generate graphic for memory usage
def graph_mem(rrd, db_type):
    png = png_path + rrd[db_type] + '.png'
    db = db_path + rrd[db_type]
    rrdtool.graph(png, '--start', 'end-120000s', '--width', '400',
            "--vertical-label=Gb", "-M",
            '--watermark=OpenSAN2', '-w 800',
            "DEF:free="+ db +":free:AVERAGE",
            "DEF:cached="+ db +":cached:AVERAGE",
            "DEF:used="+ db +":used:AVERAGE",
            "AREA:free#0000FF:free\\r",
            "LINE2:cached#00FF00:cached\\r",
            "AREA:used#FF0000:used\\r")
    print('Memory graph generated')

# Generate graphic for network interfaces
def graph_net(rrd):
    ifaces = interfaces()
    for i in ifaces:
        png = png_path + i + '.' + rrd['net'] + '.png'
        db = db_path + i + '.' + rrd['net']
        rrdtool.graph(png, '--start', 'end-50000s',
            '--title', 'Network interface ' + i,
            '--width', '400', "--vertical-label=Num",
            '--slope-mode', '-m', '1', '--dynamic-labels',
            '--watermark=OpenSAN', '-w 600',
            '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:in="+ db +":in:AVERAGE",
            "DEF:out="+ db +":out:AVERAGE",
            "LINE1:in#0000FF:in",
            "LINE2:out#00FF00:out\\n",
            )
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
        create_net(rrd)
    elif db_type == 'mem':
        create_mem(rrd_db)
    elif db_type == 'cpu':
        create_cpu(rrd_db)

# Create new network DB
def create_net(rrd):
    ifaces = interfaces()
    for i in ifaces:
        rrd_db = db_path + i + '.' + rrd['net']
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
    data_sources = [ 'DS:free:DERIVE:600:U:U',
                'DS:total:DERIVE:600:U:U',
                'DS:cached:DERIVE:600:U:U',
                'DS:buffers:DERIVE:600:U:U',
                'DS:used:DERIVE:600:U:U'
                ]
    # Create network database
    rrdtool.create( rrd_db,
                 '--start', '920804400',
                 data_sources,
                 'RRA:AVERAGE:0.5:1:24',
                 'RRA:AVERAGE:0.5:6:10',
                 'RRA:AVERAGE:0.5:1:24',
                 'RRA:AVERAGE:0.5:1:24',
                 'RRA:AVERAGE:0.5:1:24' )

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
