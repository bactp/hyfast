#!/bin/bash
while true; do
    pid="$(sudo netstat -nlp | awk '$4~":'"8089"'"{ gsub(/\/.*/,"",$7); print $7 }')"
    if [[ 0 -lt $pid  ]]
    then
        sudo kill -9 $pid
    fi
   
    # Run the first Python file to generate a random list with 100 elements    
    
    python3 /app/traffic_pattern_gen.py

    # Run the second Python file to read and print each element from the list
    nohup locust -f  /app/locustfile.py --host="$TARGET_HOST" &
    
    sleep 20

    echo $"ready"
    
    curl -XPOST http://192.168.24.20:"$SVC_PORT"/swarm 
    
    sleep 86520

done

