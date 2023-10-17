#DC2-worker2 16-32-120
#stress on each core xx percentage
sleep 10
for i in 1 2 
do
    echo $"stress 80% CPU in all core for 2minutes-test time: $i"
    stress-ng -c 0 -l 85 -t 120

    echo $"stress 93% CPU in all core for 3minutes: $i"
    stress-ng -c 0 -l 93 -t 180
    sleep 
done