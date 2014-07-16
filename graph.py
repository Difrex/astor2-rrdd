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
        print('Memory graph generated')
    elif db_type == 'cpu':
        graph_cpu(rrd)
        print('Cpu graph generated')

def graph_cpu(rrd):
    png = png_path + 'cpu' + '.png'
    db = rrd
           #" rrdtool graph /var/www/luci-static/resources/cpu".. i ..".png " .. 
           #" -e now " .. 
           #" -s 'end - 6 hours' " ..
           #" -S 60" ..  
           #" --title 'CORE-" .. core.." USAGE'" .. 
           #" --vertical-label 'Percents' " ..
           #" --imgformat PNG"..
           #" --slope-mode" ..
           #" --lower-limit 0 " .. 
           #" --upper-limit 100 " .. 
           #" --rigid " ..
           #" -E " .. 
           #" -i " .. 
           #" --color CANVAS#EEEEEE " ..
           #" --color SHADEA#FFFFFF " ..
           #" --color SHADEB#FFFFFF " .. 
           #" --color BACK#CCCCCC" .. 
           #" -w 500 " .. 
           #" -h 300 " .. 
           #" --interlaced" .. 
           #" DEF:c=/var/lib/collectd/rrd/" .. hostname .. "/cpu-"..i.."/cpu-idle.rrd:value:MAX" ..  
           #" DEF:b=/var/lib/collectd/rrd/" .. hostname .. "/cpu-"..i.."/cpu-system.rrd:value:MAX" .. 
           #" DEF:a=/var/lib/collectd/rrd/" .. hostname .. "/cpu-"..i.."/cpu-user.rrd:value:MAX" .. 
           #" DEF:d=/var/lib/collectd/rrd/" .. hostname .. "/cpu-"..i.."/cpu-wait.rrd:value:MAX" .. 
           #" AREA:c#F7FF00:Idle " ..
           #" LINE1:a#200320: AREA:a#540048:User " ..
           #" LINE1:b#2cc320: AREA:b#54eb48:System " ..
           #" LINE1:b#FF0000:Wait " ..
           #" >>/dev/null 2>>/dev/null;" 


    rrdtool.graph(png, '--start', '-46000', '--width', '300', '-h', '150',
            '--vertical-label=Percents', 
            '-S 60',
            '--slope-mode',
            '--rigid',
            '--watermark=OpenSAN2',
            '--dynamic-labels',
            '--lower-limit', '0', '-E', '-i', 
            #'-r',
            '--upper-limit','100',
            'DEF:sys='+db+':sys:AVERAGE',
            'DEF:user='+db+':user:AVERAGE',
            'CDEF:s=sys,10000000,/',
            'CDEF:u=user,10000000,/',
            'AREA:u#54eb48:System',
            'AREA:s#540048:User'
            )
 
 

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
