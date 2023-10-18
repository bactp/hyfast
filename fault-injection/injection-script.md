## 1. Stress host or VM
### stress CPU on host level
sequentially working through all the different CPU stress methods
```
stress-ng --timeout 5s --cpu 0
```
specific cpu

```
stress-ng --cpu 20 --timeout 150s --metrics-brief stress-ng --cpu 28 --timeout 180s --metrics-brief stress-ng --cpu 30 --timeout 300s --metrics-brief
```


### stress DISK on host level
continually writing, reading and removing temporary files.
```
stress-ng --hdd 4 --timeout 60s --metrics-brief stress-ng --hdd 12 --timeout 120s --metrics-brief stress-ng --hdd 22 --timeout 120s --metrics-brief stress-ng --hdd 28 --timeout 120s --metrics-brief stress-ng --hdd 29 --timeout 120s --metrics-brief stress-ng --hdd 0 --timeout 60s --metrics-brief
```

runs 2 instances of the mixed I/O stressors using a total of 10% of the available file system space for 10 minutes. Each stressor will use 5% of the available file system space.
```
stress-ng --iomix 2 --iomix-bytes 10% -t 10m
```


### stress memory
The --brk (expand heap break point), --stack (expand stack), --bigheap stressors try to rapidly consume memory

```
stress-ng --brk 2 --stack 2 --bigheap 2 -t 60s --metrics-brief 
stress-ng --brk 5 --stack 5 --bigheap 5 -t 180s --metrics-brief 
stress-ng --brk 4 --stack 4 --bigheap 4 -t 180s --metrics-brief
```
virtual mem start 2 workers spinning on anonymous mmap, allocate 1G bytes per vm worker, allocate 2x2G for vm + 2x2G for mmap

```
stress-ng --vm 2 --vm-bytes 2G --mmap 2 --mmap-bytes 2G --page-in --timeout 60s stress-ng --vm 2 --vm-bytes 2G --mmap 2 --mmap-bytes 2G --page-in --timeout 120s stress-ng --vm 3 --vm-bytes 5G --mmap 3 --mmap-bytes 5G --page-in --timeout 120s
```

run 8 virtual memory stressors that combined use 80% of the available memory for 1 hour. Thus each stressor uses 10% of the available memory
```
stress-ng --vm 9 --vm-bytes 90% -t 3m
```
### stress thermal
```
stress thermal stress-ng --matrix 0 --matrix-size 64 --tz -t 60 --log-brief
```

### ALL together
To run for 60 seconds with 4 cpu stressors, 2 io stressors and 1 vm stressor using 1GB of virtual memory, enter:

```
stress-ng --cpu 16 --io 9 --hdd 12 --vm 12 --vm-bytes 85% --timeout 180s --metrics-brief stress-ng --cpu 28 --io 12 --hdd 15 --vm 15 --vm-bytes 85% --timeout 180s --metrics-brief
```
## 2. Stress network (host/VM/container-cni0)
Add latency on network interface tc qdisc add dev ens3 root netem delay 500ms

### latency
```
tc qdisc del dev ens3 root netem
```
### Traffic drop

```
iptables - A INPUT - s 192.168 .1 .202 / 255.255 .255 .255 - j DROP

iptables - D INPUT - s 192.168 .1 .202 / 255.255 .255 .255 - j DROP
```
### Packet loss
```
tc qdisc add dev ens3 root netem loss 10%

tc qdisc del dev eth0 root netem loss 10%
```

### bandwith limit
``` 
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms

tc qdisc del dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms
```