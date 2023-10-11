import requests
import json
import time, datetime
import sys
import csv
import os
from minio import Minio

def warehouse_connection():
    client = Minio("192.168.24.20:30256",
                    access_key="XwMptXNrhYWMHj99",
                    secret_key="Uatsl7MkYaJVrABZAXRTXfQzbzJ9IwlW",
                    secure=False,
    )
    
    return client

def app_qos_query(URL, cluster_name, namespace, destination_workload):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID': cluster_name}
    ns =  namespace
    dest = destination_workload
    app_qos_metrics = {
            'request_per_second': 'round(sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"'+ ns + '",destination_workload=~"' + dest +'"}[5m])), 0.001)',
            'incoming_success_rate': 'sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"' + ns + '",destination_workload=~"' + dest +'", response_code!~"5.*"}[5m])) / \
                                      sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"'+ ns +'",destination_workload=~"' + dest +'"}[5m]))',
            'latency': '(histogram_quantile(0.95, sum(irate(istio_request_duration_milliseconds_bucket{reporter=~"destination",destination_workload=~"' + dest +'", destination_workload_namespace=~"' + ns + '"}[5m])) by (le)) / 1000) or histogram_quantile(0.95, sum(irate(istio_request_duration_seconds_bucket{reporter=~"destination",destination_workload=~"' + dest + '", destination_workload_namespace=~"'+ ns + '"}[5m])) by (le))',
            }
    
    rows = []
    for metric_name, metric_value in app_qos_metrics.items():
        r1 = requests.get(URL, headers=headers, params={'query': metric_value})
        r1_json = r1.json()['data']['result']
        
        value = r1_json[0]['value'][1]
        rows.append(value)
    
    ts = str(time.time())
    rows.append(ts)
    return rows
    
    return rows

def create_new_csv(metrics_name, cluster_name, name_space,):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{cluster_name}_{name_space}_app_data_{current_date}.csv"
    with open(file_name, mode='w', newline='') as f:
            write = csv.writer(f)
            write.writerow(metrics_name)
    return file_name


metrics_name = ['request_per_second',
                'incoming_success_rate',
                'latency',
                'timestamp' ]

URL = os.getenv("URL")
cluster_name =  os.getenv("CLUSTER_NAME") #declare as name of the cluster in container image
name_space = os.getenv("NAME_SPACE") #declare as name of namespace in container image
destination_workload = os.getenv("DEST_WORKLOAD")

# URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
# cluster_name = "data-center1"
# name_space = "sock-shop"
# destination_workload = "front-end"

current_day = None
csv_file_name = None


while True:
    """ Query data every 10 seconds """
    
    now = datetime.datetime.now()
    current_date = now.strftime("%Y%m%d")

    # Check if the day has changed
    if current_date != current_day:
        if csv_file_name:
            print(f"Closing file: {csv_file_name}")
            current_day = current_date

            #Upload to storage
            minioClient = warehouse_connection()
            path = cluster_name + "_" + name_space + "_app_data/" + current_day
            minioClient.fput_object(cluster_name, path, csv_file_name, content_type='application/csv')
            print(f"File: {csv_file_name} is uploaded to storage")
            os.remove(csv_file_name)

            csv_file_name = None

        # Create a new CSV file
        csv_file_name = create_new_csv(metrics_name, cluster_name, name_space)
        print(f"New file created: {csv_file_name}")

    # Simulate writing data to the CSV file
    with open(csv_file_name, mode='a', newline='') as f:
                write = csv.writer(f)
                rows =  []
                data = app_qos_query(URL, cluster_name, name_space, destination_workload)
                rows.append(data)
                write.writerows(rows)
                
    current_day = current_date
    time.sleep(10)

         

