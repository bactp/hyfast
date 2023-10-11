#!/bin/bash

while true; do
    # Run the first Python file to generate a random list with 100 elements    
    python3 /app/traffic_pattern_gen.py

    # Run the second Python file to read and print each element from the list
    locust -f /app/locustfile.py

    #remove the last pattern file
    rm num_reqs.csv
    # Add a delay (e.g., 5 seconds) before re-running the process
    sleep 3
done

