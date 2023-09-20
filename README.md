# Deploying Redpanda on Kubernetes k3

- https://docs.redpanda.com/current/deploy/deployment-option/self-hosted/kubernetes/kubernetes-best-practices/#use-externaldns-for-external-access

- Kind

```bash

curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind --version 



```

- Create Kind Cluster

```yaml
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
  - role: control-plane
  - role: worker
  - role: worker
  - role: worker


kind create cluster --config kind.yaml
```

- Install Redpanda

```bash
# Cert-Manager
helm repo add redpanda https://charts.redpanda.com
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager  --set installCRDs=true --namespace cert-manager  --create-namespace



# Install Redpanda

export DOMAIN=customredpandadomain.local && \
helm repo add redpanda https://charts.redpanda.com/
helm repo update
helm install redpanda redpanda/redpanda \
  --namespace crud \
  --create-namespace \
  --set external.domain=${DOMAIN} \
  --set statefulset.initContainers.setDataDirOwnership.enabled=true

# Check TLS Certs for Redpanda - 4 certs
kubectl get certificate -n crud

# Wait for Cluster to be ready

kubectl --namespace crud rollout status statefulset redpanda --watch
```

- Interact with Redpanda

```bash
alias rpk-topic="kubectl --namespace crud exec -i -t redpanda-0 -c redpanda -- rpk topic -X brokers=redpanda-0.redpanda.crud.svc.cluster.local.:9093,redpanda-1.redpanda.crud.svc.cluster.local.:9093,redpanda-2.redpanda.crud.svc.cluster.local.:9093 --tls-truststore /etc/tls/certs/default/ca.crt --tls-enabled"

rpk-topic create twitch_chat

rpk-topic describe twitch_chat

# Produce Msgs
rpk-topic produce twitch_chat
 > hello world > enter
 > second msg  > enter

# Consume
rpk-topic consume twitch_chat --num 2

# Web UI
kubectl -n redpanda port-forward svc/redpanda-console 8080:8080

rpk-topic delete twitch_chat


```

## ISSUES HERE and Below - once Cluster setup need to figure out how to have seperate App like a Python/java app Produce Messages and Consume Events from Redpanda

- Sample Consumer

```bash
# None of this works , need to figure out how to connect to Redpanda from outside the cluster

#  Fetch Cert from RP to local
kubectl get secret redpanda-default-root-certificate -n crud -o jsonpath="{.data['ca\.crt']}" | base64 -d > client-ca.crt


kubectl create secret generic redpanda-ca-cert --from-file=ca.crt=client-ca.crt -n crud



# Make Redpanda TLS Cert Available as Secret 
kubectl create secret generic redpanda-ca-cert --from-file=ca.crt -n crud


docker build -t producer-image .

# Load into Kind
kind load docker-image producer-image

kubectl apply -f producer-deployment.yaml -n crud        

kubectl logs -l app=producer -n crud


kubectl get pods -n crud  

kubectl exec -it producer-deployment-85fcf967d9-t4c9r  -n crud -- /bin/sh

kind delete cluster --name=kind


```