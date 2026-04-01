# Lab 10 - Helm Package Manager

## 1. Chart Overview

Chart path: `k8s/devops-info`.

Structure:
- `Chart.yaml`: chart metadata.
- `values.yaml`: base defaults.
- `values-dev.yaml`: dev profile (1 replica, NodePort, smaller resources).
- `values-prod.yaml`: prod profile (3 replicas, LoadBalancer, stronger resources).
- `templates/deployment.yaml`: app Deployment template.
- `templates/service.yaml`: Service template.
- `templates/_helpers.tpl`: names and common labels.
- `templates/hooks/pre-install-job.yaml`: pre-install hook.
- `templates/hooks/post-install-job.yaml`: post-install hook.

Values strategy:
- Base config in `values.yaml`.
- Environment overrides via `-f values-dev.yaml` / `-f values-prod.yaml`.

## 2. Configuration Guide

Important values:
- `replicaCount`
- `image.repository`, `image.tag`, `image.pullPolicy`
- `service.type`, `service.port`, `service.targetPort`, `service.nodePort`
- `resources.requests`, `resources.limits`
- `livenessProbe`, `readinessProbe`
- `env.PORT`, `env.LOG_FORMAT`, `env.RELEASE_VERSION`

Install examples:

```bash
# dev
helm install devops-info-lab10 k8s/devops-info \
  -n devops-lab10 --create-namespace \
  -f k8s/devops-info/values-dev.yaml

# prod upgrade
helm upgrade devops-info-lab10 k8s/devops-info \
  -n devops-lab10 \
  -f k8s/devops-info/values-prod.yaml
```

## 3. Hook Implementation

Implemented hooks:
- `pre-install` (weight `-5`): pre-check job.
- `post-install` (weight `5`): smoke-test job.

Deletion policy for both hooks:
- `hook-succeeded`

Rendered hook annotations (`helm get hooks`):

```yaml
"helm.sh/hook": pre-install
"helm.sh/hook-weight": "-5"
"helm.sh/hook-delete-policy": hook-succeeded

"helm.sh/hook": post-install
"helm.sh/hook-weight": "5"
"helm.sh/hook-delete-policy": hook-succeeded
```

Hook cleanup verification:

```bash
$ kubectl -n devops-lab10 get jobs
No resources found in devops-lab10 namespace.
```

## 4. Installation Evidence

Helm install and release list:

```bash
$ helm list -n devops-lab10
NAME                NAMESPACE     REVISION  STATUS    CHART              APP VERSION
devops-info-lab10   devops-lab10  3         deployed  devops-info-0.1.0  1.0.0
```

Kubernetes resources:

```bash
$ kubectl -n devops-lab10 get all
pod/devops-info-lab10-...                 1/1 Running
service/devops-info-lab10                 LoadBalancer 80:30081/TCP
deployment.apps/devops-info-lab10         3/3
replicaset.apps/devops-info-lab10-...     3
```

Dev vs prod:
- Dev install: `replicaCount=1`, service `NodePort`.
- Prod upgrade: `replicaCount=3`, service `LoadBalancer`, increased resources.

## 5. Operations

Used commands:

```bash
helm lint k8s/devops-info
helm template test-release k8s/devops-info
helm install --dry-run --debug test-release k8s/devops-info -n devops-lab10 --create-namespace

helm install devops-info-lab10 k8s/devops-info -n devops-lab10 --create-namespace -f k8s/devops-info/values-dev.yaml
helm upgrade devops-info-lab10 k8s/devops-info -n devops-lab10 -f k8s/devops-info/values-prod.yaml

helm history devops-info-lab10 -n devops-lab10
helm rollback devops-info-lab10 1 -n devops-lab10
helm uninstall devops-info-lab10 -n devops-lab10
```

## 6. Testing and Validation

Helm fundamentals:

```bash
$ helm version
version.BuildInfo{Version:"v4.0.0", ...}

$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories

$ helm search repo prometheus-community/prometheus | head -n 1
prometheus-community/prometheus  28.14.1  v3.10.0

$ helm show chart prometheus-community/prometheus
apiVersion: v2
appVersion: v3.10.0
description: Prometheus is a monitoring system and time series database.
```

Chart checks:

```bash
$ helm lint k8s/devops-info
1 chart(s) linted, 0 chart(s) failed

$ helm template test-release k8s/devops-info > /tmp/lab10-template.yaml
$ wc -l /tmp/lab10-template.yaml
157 /tmp/lab10-template.yaml

$ helm install --dry-run --debug test-release k8s/devops-info -n devops-lab10 --create-namespace
STATUS: pending-install
DESCRIPTION: Dry run complete
```

Accessibility check:

```bash
$ kubectl -n devops-lab10 port-forward svc/devops-info-lab10 18080:80
$ curl -sSf http://127.0.0.1:18080/health
{"status":"healthy", ...}
```
