kubeadm reset -f

rm -rf /etc/cni /etc/kubernetes /var/lib/dockershim /var/lib/etcd /var/lib/kubelet /var/run/kubernetes ~/.kube/*

ip link set cni0 down && ip link set flannel.1 down

ip link delete cni0 && ip link delete flannel.1

systemctl restart docker && systemctl restart kubelet

sudo kubeadm reset

sudo apt purge kubectl kubeadm kubelet kubernetes-cni -y
sudo apt autoremove
sudo rm -fr /etc/kubernetes/; sudo rm -fr ~/.kube/; sudo rm -fr /var/lib/etcd; sudo rm -rf /var/lib/cni/

sudo systemctl daemon-reload

sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X

# remove all running docker containers
docker rm -f `docker ps -a | grep "k8s_" | awk '{print $1}'`