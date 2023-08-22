l = {"container": {
    "cluster_ns_container_cpu_usage": "sum(rate(container_cpu_usage_seconds_total{namespace=\"sock-shop\", container=~\".+\", container!=\"POD\"}[30m])) by (container) * 100"       
}}
print(l["container"]["cluster_ns_container_cpu_usage"])