from rrdsys import interfaces

import os
import os.path

# RRD module
import rrdtool

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

# rrdtool create functions
# Needs to rewrite
##########################

# Check of rrd db file
def check_db(rrd, db_type):
    if db_type == 'net':
        ifaces = interfaces()
        for i in ifaces:
            rrd_db = db_path + i + '.' + rrd[db_type]
            if os.path.isfile(rrd_db) != True:
                new_db(rrd, db_type)
        return True
    else:
        rrd_db = db_path + rrd[db_type]
        return os.path.isfile(rrd_db)


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