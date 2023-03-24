#!/bin/bash
test=`curl -s -o /dev/null -w "%{http_code}"  http://www.msftconnecttest.com/connecttest.txt`
log=/var/log/checkinternet.log
timestamp=`date`
#echo $test
if [ $test != "200" ] ; then
	echo $timestamp " No internet - restart" >> $log
	systemctl restart networking
	systemctl restart ssh
else
	echo $timestamp " Internet is fine" >> $log
fi

