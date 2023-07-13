References:
- https://min.io/directpv 
- https://github.com/minio/directpv/blob/master/docs/cli.md 
- https://www.adaltas.com/en/2022/07/09/s3-object-storage-minio/

# Before installing
First, create the MinIO Tenant namespace. Tenants are MinIO object storage consumers. Each namespace holds one MinIO tenant at most.

1. Install Krew
```
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)
```

2. Add Krew to PATH.
```
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
```
3. Verify that Krew's install is successful by updating the plugin index
```
kubectl krew update
```

# Preparing drives for MinIO with DirectPV

1. Install the kubectl DirectPV plugin.

```
kubectl krew install directpv
```
run `kubectl directpv --version` to verify that the installation worked
If the error `Error: unknown command "directpv" for "kubectl"` is shown, try adding `$HOME/.krew/bin` to your $PATH

2. Use the plugin to install DirectPV in your k8s cluster.
```
kubectl directpv install
```

Waiting for DirectPV to initialize, the example results
```
directpv                            controller-96df4f746-22p9h                                       3/3     Running   0          3m31s   10.244.3.2      hyfast-storage-node   <none>           <none>
directpv                            controller-96df4f746-cndj5                                       3/3     Running   0          3m31s   10.244.1.8      hyfast-mgmt-node      <none>           <none>
directpv                            controller-96df4f746-r6n2v                                       3/3     Running   0          3m31s   10.244.2.3      hyfast-fmas-node      <none>           <none>
directpv                            node-server-5mhrm                                                4/4     Running   0          3m31s   10.244.1.9      hyfast-mgmt-node      <none>           <none>
directpv                            node-server-9wkb2                                                4/4     Running   0          3m31s   10.244.3.3      hyfast-storage-node   <none>           <none>
directpv                            node-server-dq878                                                4/4     Running   0          3m31s   10.244.2.2      hyfast-fmas-node      <none>           <none>

```

Ensure that DirectPV has successfully started
```
kubectl directpv info
```

3. List discoverd drives
```
kubectl directpv discover
```
This will list all available drives in the kubernetes cluster and will generate an init config file (default: drives.yaml) to initialize these drives.
```
Discovered node 'hyfast-fmas-node' ✔
 Discovered node 'hyfast-mgmt-node' ✔
 Discovered node 'hyfast-storage-node' ✔

┌─────────────────────┬──────────────────┬───────┬─────────┬────────────┬──────────────────────────────┬───────────┬─────────────┐
│ ID                  │ NODE             │ DRIVE │ SIZE    │ FILESYSTEM │ MAKE                         │ AVAILABLE │ DESCRIPTION │
├─────────────────────┼──────────────────┼───────┼─────────┼────────────┼──────────────────────────────┼───────────┼─────────────┤
│ 8:17$58/l+rVSr3z... │ hyfast-mgmt-node │ sdb1  │ 30 GiB  │ xfs        │ DELL PERC_H730P_Adp (Part 1) │ YES       │ -           │
│ 8:18$iqW4VjeQbjv... │ hyfast-mgmt-node │ sdb2  │ 30 GiB  │ xfs        │ DELL PERC_H730P_Adp (Part 2) │ YES       │ -           │
│ 8:19$ACkIu4iQSLd... │ hyfast-mgmt-node │ sdb3  │ 600 GiB │ xfs        │ DELL PERC_H730P_Adp (Part 3) │ YES       │ -           │
│ 8:20$aK0vEx40YO2... │ hyfast-mgmt-node │ sdb4  │ 234 GiB │ xfs        │ DELL PERC_H730P_Adp (Part 4) │ YES       │ -           │
└─────────────────────┴──────────────────┴───────┴─────────┴────────────┴──────────────────────────────┴───────────┴─────────────┘

Generated 'drives.yaml' successfully.
```

If you also wish to see Unavailable disks, use the --all option
```
kubectl directpv discover --all
```
```
Discovered node 'hyfast-fmas-node' ✔
 Discovered node 'hyfast-mgmt-node' ✔
 Discovered node 'hyfast-storage-node' ✔

┌─────────────────────┬─────────────────────┬───────┬──────────┬─────────────┬──────────────────────────────────┬───────────┬──────────────────────┐
│ ID                  │ NODE                │ DRIVE │ SIZE     │ FILESYSTEM  │ MAKE                             │ AVAILABLE │ DESCRIPTION          │
├─────────────────────┼─────────────────────┼───────┼──────────┼─────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ 253:0$bzQ4+cf0Dc... │ hyfast-fmas-node    │ dm-0  │ 100 GiB  │ ext4        │ ubuntu--vg-ubuntu--lv            │ NO        │ Mounted              │
│ 8:0$lkhC//oXAQ6C... │ hyfast-fmas-node    │ sda   │ 894 GiB  │ -           │ DELL PERC_H755_Front             │ NO        │ Partitioned          │
│ 8:1$oub1vctiZp71... │ hyfast-fmas-node    │ sda1  │ 1.0 GiB  │ vfat        │ DELL PERC_H755_Front (Part 1)    │ NO        │ Mounted              │
│ 8:2$90LXih+hMTcg... │ hyfast-fmas-node    │ sda2  │ 2.0 GiB  │ ext4        │ DELL PERC_H755_Front (Part 2)    │ NO        │ Mounted              │
│ 8:3$qsKBSDFYp2KB... │ hyfast-fmas-node    │ sda3  │ 891 GiB  │ LVM2_member │ DELL PERC_H755_Front (Part 3)    │ NO        │ Held by other device │
│ 253:0$+VVC+DlJjQ... │ hyfast-mgmt-node    │ dm-0  │ 100 GiB  │ ext4        │ ubuntu--vg-ubuntu--lv            │ NO        │ Mounted              │
│ 8:0$1w7neFlV3YYL... │ hyfast-mgmt-node    │ sda   │ 894 GiB  │ -           │ DELL PERC_H730P_Adp              │ NO        │ Partitioned          │
│ 8:1$xDnSjW7FaA1b... │ hyfast-mgmt-node    │ sda1  │ 1.0 GiB  │ vfat        │ DELL PERC_H730P_Adp (Part 1)     │ NO        │ Mounted              │
│ 8:2$LAmcSsJ8gVfp... │ hyfast-mgmt-node    │ sda2  │ 2.0 GiB  │ ext4        │ DELL PERC_H730P_Adp (Part 2)     │ NO        │ Mounted              │
│ 8:3$mAmnYWe0XzVU... │ hyfast-mgmt-node    │ sda3  │ 891 GiB  │ LVM2_member │ DELL PERC_H730P_Adp (Part 3)     │ NO        │ Held by other device │
│ 8:16$fhRi+Swy7ng... │ hyfast-mgmt-node    │ sdb   │ 894 GiB  │ -           │ DELL PERC_H730P_Adp              │ NO        │ Partitioned          │
│ 8:17$58/l+rVSr3z... │ hyfast-mgmt-node    │ sdb1  │ 30 GiB   │ xfs         │ DELL PERC_H730P_Adp (Part 1)     │ YES       │ -                    │
│ 8:18$iqW4VjeQbjv... │ hyfast-mgmt-node    │ sdb2  │ 30 GiB   │ xfs         │ DELL PERC_H730P_Adp (Part 2)     │ YES       │ -                    │
│ 8:19$ACkIu4iQSLd... │ hyfast-mgmt-node    │ sdb3  │ 600 GiB  │ xfs         │ DELL PERC_H730P_Adp (Part 3)     │ YES       │ -                    │
│ 8:20$aK0vEx40YO2... │ hyfast-mgmt-node    │ sdb4  │ 234 GiB  │ xfs         │ DELL PERC_H730P_Adp (Part 4)     │ YES       │ -                    │
│ 11:0$+n+gGN16BfB... │ hyfast-mgmt-node    │ sr0   │ 1024 MiB │ -           │ HL-DT-ST HL-DT-ST_DVD+_-RW_GU90N │ NO        │ CDROM                │
│ 253:0$hNz3ToIZpJ... │ hyfast-storage-node │ dm-0  │ 100 GiB  │ ext4        │ ubuntu--vg-ubuntu--lv            │ NO        │ Mounted              │
│ 8:0$Q7Dz7Lny5tL0... │ hyfast-storage-node │ sda   │ 894 GiB  │ -           │ DELL PERC_H755_Front             │ NO        │ Partitioned          │
│ 8:1$6es084/bV5vq... │ hyfast-storage-node │ sda1  │ 1.0 GiB  │ vfat        │ DELL PERC_H755_Front (Part 1)    │ NO        │ Mounted              │
│ 8:2$CkBdFNjmXxFO... │ hyfast-storage-node │ sda2  │ 2.0 GiB  │ ext4        │ DELL PERC_H755_Front (Part 2)    │ NO        │ Mounted              │
│ 8:3$wvamTObC+ztc... │ hyfast-storage-node │ sda3  │ 891 GiB  │ LVM2_member │ DELL PERC_H755_Front (Part 3)    │ NO        │ Held by other device │
└─────────────────────┴─────────────────────┴───────┴──────────┴─────────────┴──────────────────────────────────┴───────────┴──────────────────────┘

Generated 'drives.yaml' successfully.
```

4. Intitialize the drives:

```
kubectl directpv init drives.yaml --dangerous
```
This will initialize selected drives in drives.yaml
NOTE:
initialization will erase all data on the drives. Double check to make sure that only intended drives are specified
```
███████████████████████████████████████████████████████████████████████████ 100%

 Processed initialization request 'f926f2cd-6e6e-4cc8-9412-5ff6a6ccea54' for node 'hyfast-storage-node02' ✔

┌──────────────────────────────────────┬───────────────────────┬───────┬─────────┐
│ REQUEST_ID                           │ NODE                  │ DRIVE │ MESSAGE │
├──────────────────────────────────────┼───────────────────────┼───────┼─────────┤
│ f926f2cd-6e6e-4cc8-9412-5ff6a6ccea54 │ hyfast-storage-node02 │ sdb1  │ Success │
│ f926f2cd-6e6e-4cc8-9412-5ff6a6ccea54 │ hyfast-storage-node02 │ sdb2  │ Success │
│ f926f2cd-6e6e-4cc8-9412-5ff6a6ccea54 │ hyfast-storage-node02 │ sdb3  │ Success │
│ f926f2cd-6e6e-4cc8-9412-5ff6a6ccea54 │ hyfast-storage-node02 │ sdb4  │ Success │
└──────────────────────────────────────┴───────────────────────┴───────┴─────────┘

```

5. Verify installation
```
kubectl directpv info
```
This will show information about the drives formatted and added to DirectPV

```
┌─────────────────────────┬──────────┬───────────┬─────────┬────────┐
│ NODE                    │ CAPACITY │ ALLOCATED │ VOLUMES │ DRIVES │
├─────────────────────────┼──────────┼───────────┼─────────┼────────┤
│ • hyfast-fmas-node      │ -        │ -         │ -       │ -      │
│ • hyfast-mgmt-node      │ -        │ -         │ -       │ -      │
│ • hyfast-storage-node02 │ 1.7 TiB  │ 0 B       │ 0       │ 4      │
└─────────────────────────┴──────────┴───────────┴─────────┴────────┘

0 B/1.7 TiB used, 0 volumes, 4 drives

```

6. Change directpv-min-io to default storage class
```
kubectl patch storageclass directpv-min-io -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

# Installing MinIO Operator with krew
Proceed to install the minio Krew plugin and initialize the MinIO Operator

```
kubectl krew install minio
kubectl minio init
```
Edit console service in minio-operator namespace
```
kubectl edit svc console -n minio-operator
```
Login Token
```
kubectl -n minio-operator get secret $(kubectl -n minio-operator get serviceaccount console-sa -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode
```
```
SA_TOKEN=$(kubectl -n minio-operator  get secret console-sa-secret -o jsonpath="{.data.token}" | base64 --decode)
echo $SA_TOKEN
```

```
kubectl -n minio-operator  get secret console-sa-secret -o jsonpath="{.data.token}" | base64 --decode
```

```
eyJhbGciOiJSUzI1NiIsImtpZCI6IjVMRkhyVXVtMDRMVGFNRk02b1hUUFZUMW1Ec2k3MFVNa3NyUkZJVWJucTgifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtaW5pby1vcGVyYXRvciIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJjb25zb2xlLXNhLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJjb25zb2xlLXNhIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYzRhYjJiYTktOTExZC00MDNhLTlmZDctNWFiODNmMTBmZTU5Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Om1pbmlvLW9wZXJhdG9yOmNvbnNvbGUtc2EifQ.Hl2BRouEQPKPJwID9ESRWpvpDwivuxFW3ab0aGKHPup91MkpiyMsgFoE77TT5NBnxiiOx7B6wZGDG1TXEwu8J43YHo-gZlIMp3f5NS_0SDRXVN1b_H1X5h9gNhxIaPXEFYesxQg0iQKBtY6jdwWtCVseukGUC83Y_kPuFcSYBGaFwiokj_ygUfUakaErh5LPVGBF79XhudlcbXGQ1TeGCiSaxT5w7sTmPTPIDO6rUbNkTJCzvYoBDbS8_wGz23BbGVouFdG2R7ET5Fum4YtHpJzGhSnukaC5S2ykgv0mZ0wU2MS75nmGm_CQ99IhLPqoK1IWTR0pMbjmRegNn2EBhQ
```

# Create new partition in linux
References: https://phoenixnap.com/kb/linux-create-partition 
Follow the steps below to partition a disk in Linux by using the fdisk command.
1. List existing partitions
```
sudo fdisk -l
```
The output contains information about storage disks and partitions:
```
evice       Start        End    Sectors   Size Type
/dev/sda1     2048    2203647    2201600   1.1G EFI System
/dev/sda2  2203648    6397951    4194304     2G Linux filesystem
/dev/sda3  6397952 1874327551 1867929600 890.7G Linux filesystem


Disk /dev/sdb: 893.77 GiB, 959656755200 bytes, 1874329600 sectors
Disk model: PERC H730P Adp  
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: 25B19FB1-4FC0-44C8-9080-06FD58D7EC68
```

2. Select Storage Disk

Select the storage disk you want to create partitions on by running the following command:
```
sudo fdisk /dev/sdb
```

3. Create new partition
- enter `n` commnand to create a new partition
- Select the partition number by typing the default number
- After that, you are asked for the starting and ending sector of your hard drive. It is best to type the default number in this section
creat partitions linux
- The last prompt is related to the size of the partition. You can choose to have several sectors or to set the size in megabytes or gigabytes.  Example Type +2G to set the size of the partition to 2G.
- write on disk by enter `w` and quit

4. Verify that partition is created by running the following cmd:
```
sudo fdisk -l
```

Get token for Minio Operator login
```
kubectl -n minio-operator get secret $(kubectl -n minio-operator get serviceaccount console-sa -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode

```