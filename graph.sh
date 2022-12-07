#!/bin/bash
rrd_file=/opt/radioclock/radioclock/temp-out.rrd
temp_graph=/var/www/graph/temp/temp
humid_graph=/var/www/graph/humid/humid
d_date=$(date +%F)
ts_end=`date +%s`
ts_start=`date -d "-1 day" +%s`
# GENERATE GRAPHS
rrdtool graph $temp_graph-$d_date.png --start $ts_start --end $ts_end DEF:temp_in=$rrd_file:temp_in:AVERAGE DEF:temp_out=$rrd_file:temp_out:AVERAGE LINE2:temp_in#0000FF:temp_in LINE2:temp_out#00FF00:temp_out
rrdtool graph $humid_graph-$d_date.png --start $ts_start --end $ts_end DEF:temp_in=$rrd_file:temp_in:AVERAGE DEF:temp_out=$rrd_file:temp_out:AVERAGE DEF:humid=$rrd_file:humid:AVERAGE LINE2:temp_in#0000FF:temp_in LINE2:temp_out#00FF00:temp_out LINE1:humid#FF0000:humid
# REMOVE OLD ONES
find /var/www/graph -type f -name "*.png" -mtime +30 -exec rm -f {} \;
