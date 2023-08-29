import requests
import time
import sys

# Prometheus api endpoint for query 
URL = "http://192.168.24.20:31179/prometheus/api/v1/query"

# Memory Query
PROMQL1 = {'query':'sum(instance:node_cpu_utilisation:rate5m) by (instance)'}

# CPU Query
PROMQL2 = {'query':'sum(instance:node_cpu:rate:sum) by (instance)'}

print("row,instance,memory,cpu")

line_no = 1
headers = {'X-Scope-OrgID':'compute-host'}

#Query every 15 seconds 100 times
for seq in range(0 , 100):
    rows = []
    row = 0

    r1 = requests.get(url = URL, headers=headers, params = PROMQL1)

    r2 = requests.get(url = URL, headers=headers, params = PROMQL2)

    r1_json = r1.json()['data']['result']
    r2_json = r2.json()['data']['result']
    

    for result in r1_json:
        l = []
        l.append(result['metric'].get('instance', ''))
        l.append(result['value'][1])
        rows.append(l)

    for result in r2_json:
        l = []
        l.append(result['value'][1])
        rows[row].append(l[0])
        row = row + 1
        
    # print(rows)
    for ro in rows:
        line = str(time.time())
        line = line + "," + ro[0] + "," + ro[1] + "," + ro[2]
        print(str(line))
        # line_no = line_no + 1

    sys.stdout.flush()
    time.sleep(15)