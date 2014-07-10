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

# System
########

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

# Get memory function
def get_mem():
    proc = '/proc/meminfo'
    mem = {}
    f = open(proc, "r")
    for line in f.readlines():
        memory = line.split()
        m = memory[0][:-1]
        if m == 'MemTotal':
            mem['total'] = memory[1]
        elif m == 'MemFree':
            mem['free'] = memory[1]
        elif m == 'Buffers':
            mem['buffers'] = memory[1]
        elif m == 'Cached':
            mem['cached'] = memory[1]
        elif m == 'SwapCached':
            mem['swap'] = memory[1]

    mem['used'] = (int( mem['total'] ) - int( mem['free'] )) - ( int(mem['cached']) - int(mem['buffers']) )
    return mem


# Get phisicals CPU
def cpu_id():
    proc = '/proc/cpuinfo'
    f = open(proc, "r")

    # Physical id counter
    phys = 1
    for line in f.readlines():
        l = line.split(':')
        name = l[0][:-1]
        if name == 'physical id':
            value = l[1]
            if int(value) >= phys:
                phys = phys + 1

    return phys


# Get CPU cores
def cpu_cores():
    proc = '/proc/cpuinfo'
    f = open(proc, 'r')

    # Cores counter
    cores = 1
    for line in f.readlines():
        l = line.split(':')
        name = re.split(r'(.+)\s\s+', l[0])
        # Exception
        try:
            if name[1] == 'core id':
                value = l[1]
                if int(value) >= cores:
                    cores = cores + 1
        except:
            continue

    print cores
    return cores


# Get system output. 
# !!! Will be removed later !!!
def get_cmd(cmd):
    import os
    return int(os.popen(cmd).read())

# End of system
###############

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
        print('Net graphs generated')
    elif db_type == 'mem':
        graph_mem(rrd, db_type)

# Generate graphic for memory usage
def graph_mem(rrd, db_type):
    png = png_path + rrd[db_type] + '.png'
    db = db_path + rrd[db_type]
    rrdtool.graph(png, '--start', '-1800', '--width', '400',
            "--vertical-label=Gb", 
            '--watermark=OpenSAN2', '-w 800', '-r',
            # '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:total="+ db +":total:AVERAGE",
            "DEF:free="+ db +":free:AVERAGE",
            "DEF:used="+ db +":used:AVERAGE",
            "AREA:total#000000:Total memory\\n",
            "AREA:used#aa0000:Used memory\\n",
            "AREA:free#00FF00:Free memory\\n" )


# Generate graphic for network interfaces
def graph_net(rrd):
    ifaces = interfaces()
    for i in ifaces:
        png = png_path + i + '.' + rrd['net'] + '.png'
        db = db_path + i + '.' + rrd['net']
        rrdtool.graph(png, '--start', 'end-6h',
            '--title', 'Network interface ' + i,
            '--width', '400', "--vertical-label=bits/s",
            '--slope-mode', '-m', '1', '--dynamic-labels',
            '--watermark=OpenSAN2', '-w 600',
            '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:in="+ db +":in:AVERAGE",
            "DEF:out="+ db +":out:AVERAGE",
            "LINE1:in#0000FF:in",
            "LINE2:out#00FF00:out\\n",
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
        create_cpu(rrd_db)

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
