#DC2-worker2 16-32-120
#stress on each core xx percentage
sleep 10
for i in 1 2 3 4
do
    echo $"stress 80% memory accumulate for 2minutes-test time: $i"
    stress-ng --vm 6 --vm-bytes 80% -t 120s

    echo $"stress 90% memory accumulate for 2minutes-test time: $i"
    stress-ng --vm 9 --vm-bytes 90% -t 180s
    sleep 10
done