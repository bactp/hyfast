#hyfast-compute02 80-156-1.5T
#stress on each core xx percentage
sleep 10
for i in 1 2 
do
    echo $"stress 89% CPU in all core for 2minutes-test time: $i"
    stress-ng -c 0 -l 89 -t 120

    echo $"stress 93% CPU in all core for 3minutes: $i"
    stress-ng -c 0 -l 93 -t 180
    sleep 
done