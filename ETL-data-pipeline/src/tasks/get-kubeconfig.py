from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()
ns = v1.list_namespace().items

ns_list = []

for n in ns:
    try:
        name = n.metadata.name
        ns_list.append(name)
    except:
        pass
print(ns_list)
# print(ns_list['items'][0]['metadata']['name'])
