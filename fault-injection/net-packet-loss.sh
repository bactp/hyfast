#DC2-worker1 16-32-120
#stress on each core xx percentage packet loss
sleep 10
for i in 1 2 3
do
    echo $"inject 70% packetloss to interface ens3 for 2minutes-test time: $i"
    tc qdisc add dev ens3 root netem loss 70% 
    sleep 120
    tc qdisc del dev ens3 root netem loss 70%

    echo $"stress 80% memory accumulate for 2minutes-test time: $i"
    tc qdisc add dev ens3 root netem loss 80% 
    sleep 180
    tc qdisc del dev ens3 root netem loss 90%
    sleep 10
done