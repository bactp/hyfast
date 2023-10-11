#!/bin/bash

# x00123430 Kevin Lambe
echo "co    N    CPU usage" >results.dat
for i in {1..50}
do
# do something here
./loadtest $i &
cpu=`mpstat 5 1 -o JSON | jq '100 - .sysstat.hosts[0].statistics[0]."cpu-load"[0].idle'`


#sleep 5
pkill loadtest
cnt=`grep processor /proc/cpuinfo | wc -l`
num=`cat synthetic.dat |wc -l`
echo "Finished run $i co is $num num processors is $cnt"
echo "$num    $i    $cpu" >>results.dat
echo "$num    $i    $cpu"

done




#./loadtest $1 &
#sleep $2
#pkill loadtest


#NUM=`wc -l "$synthetic.dat"`
