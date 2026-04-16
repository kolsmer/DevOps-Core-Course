# Lab 13 - ArgoCD GitOps

## 1. ArgoCD Setup

Installed via Helm in `argocd` namespace.

```bash
helm install argocd argo/argo-cd -n argocd --wait --timeout 600s
kubectl -n argocd get pods
```

All core pods are running:
- argocd-application-controller
- argocd-applicationset-controller
- argocd-dex-server
- argocd-notifications-controller
- argocd-redis
- argocd-repo-server
- argocd-server

UI access:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

CLI access:

```bash
argocd login localhost:8080 --username admin --password <password> --insecure --grpc-web
argocd app list --grpc-web
```

## 2. Applications

Application manifests:
- `k8s/argocd/application.yaml`
- `k8s/argocd/application-dev.yaml`
- `k8s/argocd/application-prod.yaml`

Source:
- repo: `https://github.com/kolsmer/DevOps-Core-Course.git`
- path: `k8s/devops-info`
- branch: `lab13`

Destinations:
- base app: `devops-lab13`
- dev app: `dev`
- prod app: `prod`

## 3. Multi-Environment

Dev:
- file: `values-dev.yaml`
- sync policy: automated + prune + selfHeal
- namespace: `dev`
- final state: `1/1` replicas, healthy

Prod:
- file: `values-prod.yaml`
- sync policy: manual
- namespace: `prod`
- final state: `3/3` replicas, healthy

Base app:
- file: `values.yaml`
- namespace: `devops-lab13`
- manual sync

## 4. Self-Healing

Dev auto-sync test:

```bash
$ date '+before %F %T'
before 2026-04-16 14:45:57
$ kubectl -n dev scale deployment/devops-info-dev --replicas=5
$ kubectl -n dev get deploy devops-info-dev
1/5
$ date '+after %F %T'
after 2026-04-16 14:46:17
$ kubectl -n dev get deploy devops-info-dev
1/1
```

Result:
- ArgoCD auto-healed dev deployment back to Git state.
- Kubernetes still handles pod recreation when a pod is deleted.

Sync behavior:
- ArgoCD polls Git periodically and also reacts to sync actions.
- Dev app auto-syncs because `automated.selfHeal=true`.
- Prod stays manual.

## 5. Final Status

```bash
$ argocd app list --grpc-web
argocd/devops-info-dev    Synced  Healthy  Auto-Prune
argocd/devops-info-lab13  Synced  Healthy  Manual
argocd/devops-info-prod   Synced  Healthy  Manual
```

Deployments:
- `dev`: `devops-info-dev` = `1/1`
- `prod`: `devops-info-prod` = `3/3`
- `devops-lab13`: `devops-info-lab13` = `3/3`

## 6. Screenshots

- ArgoCD applications list: [argo-applications-list.png](screenshots/argo-applications-list.png)
- Dev app details: [dev-details.png](screenshots/dev-details.png)
- Prod app details: [prod-details.png](screenshots/prod-details.png)

## 7. Notes

Why prod manual:
- safer release control
- review before deployment
- fewer accidental production changes
