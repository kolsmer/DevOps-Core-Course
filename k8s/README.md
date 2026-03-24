# Lab 9 — Kubernetes Fundamentals

## 1. Architecture Overview

- Local cluster: `kind` (`kind-lab09`, Kubernetes `v1.33.1`)
- Namespace: `devops-lab09`
- Workload: `Deployment/devops-info`
- Replicas: `3` (scaled to `5` during Task 4)
- Exposure: `Service/devops-info` (`NodePort`, `80 -> 8000`, node port `30080`)
- Access flow: `localhost:30080 -> Service -> Pods`

Resource strategy:
- requests: `100m CPU`, `128Mi memory`
- limits: `200m CPU`, `256Mi memory`

## 2. Manifest Files

- `k8s/namespace.yml`: dedicated namespace for isolation.
- `k8s/deployment.yml`: app Deployment, 3 replicas, rolling update strategy, probes, resources.
- `k8s/service.yml`: NodePort Service for local access from host.
- `k8s/kind-config.yaml`: kind cluster config with host port mapping for `30080`.

Key choices:
- `maxUnavailable: 0` and `maxSurge: 1` to keep availability during rollout.
- readiness/liveness on `/health` for fast fail detection.
- `imagePullPolicy: IfNotPresent` + `kind load docker-image` for local image usage.

## 3. Deployment Evidence

Cluster setup:

```bash
$ kubectl cluster-info --context kind-lab09
Kubernetes control plane is running at https://127.0.0.1:42241
CoreDNS is running at https://127.0.0.1:42241/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

$ kubectl get nodes --context kind-lab09
NAME                  STATUS   ROLES           AGE     VERSION
lab09-control-plane   Ready    control-plane   7m22s   v1.33.1
```

Deployment state:

```bash
$ kubectl -n devops-lab09 get all -o wide
pod/devops-info-...   1/1 Running ... (3 pods)
service/devops-info   NodePort 10.96.168.127 80:30080/TCP
deployment.apps/devops-info   3/3 available
```

Pods and service:

```bash
$ kubectl -n devops-lab09 get pods,svc -o wide
NAME                               READY STATUS  IP
pod/devops-info-...                1/1   Running 10.244.0.x
service/devops-info                NodePort 80:30080/TCP
```

Deployment details:

```bash
$ kubectl -n devops-lab09 describe deployment devops-info
Replicas:               3 desired | 3 updated | 3 total | 3 available
StrategyType:           RollingUpdate
RollingUpdateStrategy:  0 max unavailable, 1 max surge
Liveness:   http-get http://:8000/health ...
Readiness:  http-get http://:8000/health ...
```

Service connectivity:

```bash
$ curl -sSf http://localhost:30080/health
{"status":"healthy", ...}

$ curl -sSf http://localhost:30080/ | head -c 220
{"service":{"name":"devops-info-service","version":"1.0.0",...}
```

## 4. Operations Performed

Deploy:

```bash
docker build -t devops-info-service:latest ./app_python
kind load docker-image devops-info-service:latest --name lab09
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl -n devops-lab09 rollout status deployment/devops-info
```

Scale to 5:

```bash
$ kubectl -n devops-lab09 scale deployment/devops-info --replicas=5
$ kubectl -n devops-lab09 get deployment devops-info
NAME          READY   UP-TO-DATE   AVAILABLE
devops-info   5/5     5            5
```

Rolling update (config change):

```bash
$ kubectl -n devops-lab09 set env deployment/devops-info RELEASE_VERSION=v2
$ kubectl -n devops-lab09 rollout status deployment/devops-info
deployment "devops-info" successfully rolled out

$ kubectl -n devops-lab09 rollout history deployment/devops-info
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

Rollback:

```bash
$ kubectl -n devops-lab09 rollout undo deployment/devops-info
$ kubectl -n devops-lab09 rollout status deployment/devops-info
deployment "devops-info" successfully rolled out

$ kubectl -n devops-lab09 rollout history deployment/devops-info
REVISION  CHANGE-CAUSE
2         <none>
3         <none>
```

Service network check:

```bash
$ kubectl -n devops-lab09 get endpoints devops-info -o wide
devops-info   10.244.0.15:8000,10.244.0.16:8000,10.244.0.17:8000 + 2 more...
```

## 5. Production Considerations

- Health checks: readiness + liveness on `/health` to avoid routing traffic to broken pods.
- Resource controls: requests/limits prevent noisy-neighbor issues and stabilize scheduling.
- Update safety: rolling strategy keeps service available during updates.
- Improvements for production:
  - use image tags (not `latest`) and signed images
  - add HPA, PDB, NetworkPolicy
  - store config/secrets in ConfigMap/Secret
  - add Prometheus alerts and log aggregation dashboards.

## 6. Challenges & Solutions

- Local image was not pullable from cluster:
  - fixed with `kind load docker-image ...`.
- Need host access for NodePort in kind:
  - fixed with `extraPortMappings` in `k8s/kind-config.yaml`.
- Rollout verification required zero-downtime behavior:
  - used `maxUnavailable: 0` and validated with rollout status/history.

## Tool Choice

Chosen local cluster: `kind`.
Reason: fast startup, Docker-based, reproducible config, good fit for local labs and CI-like workflows.
