from rrdsys import interfaces

# RRD module
import rrdtool

# Create graph functions
########################

db_path = '/var/lib/astor2-rrdd/rrd/'
png_path = '/var/lib/astor2-rrdd/png/'

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
    rrdtool.graph(png, '--start', '-16000', '--width', '300', '-h', '150',
            "--vertical-label=Gb", 
            '--watermark=OpenSAN2', '-r',
            '--dynamic-labels',
            '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:total="+ db +":total:AVERAGE",
            "DEF:free="+ db +":free:AVERAGE",
            "DEF:cached="+ db +":cached:AVERAGE",
            "DEF:buffered="+ db +":buffers:AVERAGE",
            "DEF:used="+ db +":used:AVERAGE",
            "CDEF:mbuffered=used,buffered,+",
            "CDEF:mc=cached,buffered,-",
            "CDEF:mcached=mc,used,+",
            "CDEF:mfree=free,mbuffered,+",
            "AREA:total#00FF00:Free memory",
            #"AREA:mfree#00FF00:Free memory" ,
            "AREA:mcached#00fff0: Cached memory",
            "AREA:mbuffered#ffff00:Buffered memory",
            "AREA:used#aa0000:Used memory")


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
            "LINE1:out#FF0000:out",
            "LINE2:in#0000FF:in",
            )

# End of create graph functions
###############################
