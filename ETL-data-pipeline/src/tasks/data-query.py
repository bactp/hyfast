import requests
import json

url = url = 'http://192.168.24.20:31179/prometheus/api/v1/query'
metrics = 'container_cpu_cfs_throttled_seconds_total'
headers = {'X-Scope-OrgID':'central-cluster'}

response = requests.get(url, headers=headers, params={'query': metrics})

print(response.json())
metric_value = round(float(response.json()['data']['result'][0]['value'][1]),4)

print(response.json())