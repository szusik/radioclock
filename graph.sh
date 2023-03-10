#!/bin/bash
rrd_file=/opt/radioclock/radioclock/temp-out.rrd
graph_base=/var/www/graph
temp_graph=$graph_base/temp/temp
humid_graph=$graph_base/humid/humid
d_date=$(date +%F)
ts_end=`date +%s`
ts_start=`date -d "-1 day" +%s`
# GENERATE GRAPHS
rrdtool graph $temp_graph-$d_date.png --start $ts_start --end $ts_end DEF:temp_in=$rrd_file:temp_in:AVERAGE DEF:temp_out=$rrd_file:temp_out:AVERAGE LINE2:temp_in#0000FF:temp_in LINE2:temp_out#00FF00:temp_out
rrdtool graph $humid_graph-$d_date.png --start $ts_start --end $ts_end DEF:temp_in=$rrd_file:temp_in:AVERAGE DEF:temp_out=$rrd_file:temp_out:AVERAGE DEF:humid=$rrd_file:humid:AVERAGE LINE2:temp_in#0000FF:temp_in LINE2:temp_out#00FF00:temp_out LINE1:humid#FF0000:humid
# REMOVE OLD ONES
find /var/www/graph -type f -name "*.png" -mtime +60 -exec rm -f {} \;
# prepare html
html_pre='<!DOCTYPE html><html><head><link rel="stylesheet" type="text/css" href="simple-lightbox.min.css"></head><body><script src="simple-lightbox.min.js"></script><script src="jquery-3.5.1.min.js"></script>'
html_suf='<script type="text/javascript">var lightbox1 = new SimpleLightbox("a.temp",{"captionSelector":"self","captionPosition":"outside"});var lightbox2 = new SimpleLightbox("a.humid",{"captionSelector":"self","captionPosition":"outside"});</script></body></html>'

echo $html_pre > $graph_base/index.html
for f in $graph_base/*/*.png; do
graph_kind="temp"
if [[ $f == *"humid"* ]]; then
  graph_kind="humid"
fi
src=${f/\/var\/www\///}
echo '<a href="'$src'" title="'$src'" class="'$graph_kind'">'$src'</a><br/>' >> $graph_base/index.html
done
echo $html_suf >> $graph_base/index.html