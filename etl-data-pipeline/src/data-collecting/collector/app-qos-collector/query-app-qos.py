import requests
import json
import time, datetime
import sys
import csv
import os
from minio import Minio
import signal

def warehouse_connection():
    client = Minio("192.168.24.20:30256",
                    access_key="XwMptXNrhYWMHj99",
                    secret_key="Uatsl7MkYaJVrABZAXRTXfQzbzJ9IwlW",
                    secure=False,
    )
    
    return client

def app_qos_query(URL, cluster_name, namespace):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID': cluster_name}
    ns =  namespace
    app_qos_metrics = {
            'request_per_second': 'sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"'+ ns + '"}[5m])) by (destination_workload)',
            'incoming_success_rate': 'sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"' + ns + '", response_code!~"5.*"}[5m])) by (destination_workload) / \
                                      sum(irate(istio_requests_total{reporter=~"destination",destination_workload_namespace=~"'+ ns +'"}[5m])) by (destination_workload)',
            'latency': '(histogram_quantile(0.95, sum(irate(istio_request_duration_milliseconds_bucket{reporter=~"destination", destination_workload_namespace=~"' + ns + '"}[5m])) by (destination_workload,le)) / 1000) or histogram_quantile(0.95, sum(irate(istio_request_duration_seconds_bucket{reporter=~"destination", destination_workload_namespace=~"'+ ns + '"}[5m])) by (destination_workload, le))',
            }
    
    rows = []
    r0 = requests.get(url = URL, headers = headers, params = {'query': app_qos_metrics['request_per_second']})
    r0_json = r0.json()['data']['result']
    
    for result in r0_json:
        l = []
        l.append(result['metric'].get('destination_workload', ''))
        rows.append(l)
    
    for metric_name, metric_value in app_qos_metrics.items():
        r1 = requests.get(URL, headers=headers, params={'query': metric_value})
        r1_json = r1.json()['data']['result']
        
        row = 0
        for result in r1_json:
                l = []
                l.append(result['value'][1])
                rows[row].append(l[0])
                row = row + 1
    for row in rows:
        ts = str(time.time())
        row.append(ts)
    
    return rows
    

def create_new_csv(metrics_name, cluster_name, name_space,):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{cluster_name}_{name_space}_app_data_{current_date}.csv"
    with open(file_name, mode='w', newline='') as f:
            write = csv.writer(f)
            write.writerow(metrics_name)
    return file_name


metrics_name = ['service_name',
                'request_per_second',
                'incoming_success_rate',
                'latency',
                'timestamp' ]

# URL = os.getenv("URL")
# cluster_name =  os.getenv("CLUSTER_NAME") #declare as name of the cluster in container image
# name_space = os.getenv("NAME_SPACE") #declare as name of namespace in container image

URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
cluster_name = "data-center1"
name_space = "sock-shop"


current_day = None
csv_file_name = None


while True:
    try: 
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
                    data = app_qos_query(URL, cluster_name, name_space)
                    write.writerows(data)
                    
        current_day = current_date
        time.sleep(10)
    except Exception as e:
            print("reconnecting to endpoints")
            time.sleep(15)
