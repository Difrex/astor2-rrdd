from rrdsys import interfaces, get_cores_by_phys, cpus

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
            "CDEF:mcached=used,cached,+",
            "CDEF:mb=buffered,cached,-",
            "CDEF:mbuffered=mb,used,+",
            "CDEF:mfree=free,mbuffered,+",
            "AREA:total#00FF00:Free memory",
            #"AREA:mfree#00FF00:Free memory" ,
            "AREA:mbuffered#ffff00:Buffered memory",
            "AREA:mcached#00fff0: Cached memory",
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


# Generate CPU graph
def graph_cpu(rrd):
    physicals = cpus()
    cores = get_cores_by_phys()
    all_load_db = db_path + rrd['cpu']

    # generate all load avverage graphic
    png = png_path + 'All' + rrd['cpu'] + '.png'
    generate_cpu(png, all_load_db, 'All')

    # Cores processing
    # If only one physical CPU in system
    # we creating only one graphic:
    # load average by core
    if physicals == 1:
        c = 0
        while c < cores:
            pass
            c += 1


# Generate cores by cpu graph
def generate_cpu(png, db, core):
    # Rewrite this
    rrdtool.graph(png, '--start', 'end-6h',
            '--title', 'Load: ' + core, '-h', '150',
            '--width', '400', "--vertical-label=bits/s",
            '--slope-mode', '-m', '1', '--dynamic-labels',
            '--watermark=OpenSAN2',
            '--lower-limit', '0', '-E', '-i', '-r',
            "DEF:sys="+ db +":sys:AVERAGE",
            "DEF:user="+ db +":user:AVERAGE",
            "LINE1:sys#FF0000:sys",
            "LINE2:user#0000FF:user",
            )


# End of create graph functions
###############################
