# Lab 11 - Kubernetes Secrets and Vault

## 1. Kubernetes Secrets

Create secret (imperative):

```bash
kubectl -n devops-lab11 create secret generic app-credentials \
  --from-literal=username=lab11-user \
  --from-literal=password=lab11-pass
```

View secret:

```bash
$ kubectl -n devops-lab11 get secret app-credentials -o yaml
apiVersion: v1
data:
  username: bGFiMTEtdXNlcg==
  password: bGFiMTEtcGFzcw==
kind: Secret
```

Decode:

```bash
$ kubectl -n devops-lab11 get secret app-credentials -o jsonpath='{.data.username}' | base64 -d
lab11-user
$ kubectl -n devops-lab11 get secret app-credentials -o jsonpath='{.data.password}' | base64 -d
lab11-pass
```

Base64 vs encryption:
- Base64 is encoding, not protection.
- Kubernetes Secrets are not safely encrypted unless etcd encryption at rest is configured by cluster admin.

## 2. Helm Secret Integration

Chart changes:
- `templates/secrets.yaml` added.
- `templates/deployment.yaml` uses `envFrom.secretRef`.
- `templates/serviceaccount.yaml` enabled for Vault role binding.
- `values.yaml` extended with `secrets` and `vault` sections.

Verification:

```bash
$ kubectl -n devops-lab11 describe pod <pod>
Environment Variables from:
  devops-info-lab11-secret  Secret  Optional: false
```

`describe pod` shows secret reference only; plaintext values are not printed.

## 3. Resource Management

Deployment uses requests/limits:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

How values were chosen:
- Requests: baseline for stable scheduling.
- Limits: cap peak usage to protect node.
- In production tune by real metrics (CPU/memory percentiles and OOM/restart history).

## 4. Vault Integration

Install Vault (dev mode + injector):

```bash
helm install vault hashicorp/vault -n vault \
  --set server.dev.enabled=true \
  --set injector.enabled=true
```

Pods:

```bash
$ kubectl -n vault get pods
vault-0                                1/1 Running
vault-agent-injector-...               1/1 Running
```

Vault config done:
- KV v2 enabled at `kv/`.
- Secret stored at `kv/devops-lab11/devops-info`.
- Kubernetes auth enabled.
- Policy `devops-info-policy` and role `devops-info-role` created.
- Role bound to service account `devops-info-lab11` in namespace `devops-lab11`.

App release upgraded with Vault injection enabled.

Injection verification:

```bash
$ kubectl -n devops-lab11 get pod <pod> -o jsonpath='{.spec.containers[*].name}'
devops-info vault-agent

$ kubectl -n devops-lab11 exec <pod> -c devops-info -- ls /vault/secrets
app-config
```

Expected path:
- `/vault/secrets/app-config`

## 5. Security Analysis

Kubernetes Secrets:
- Pros: native, simple, fast integration.
- Cons: base64 only, depends on cluster hardening (RBAC, etcd encryption).

Vault:
- Pros: centralized policies, audit trail, dynamic auth, controlled access.
- Cons: extra operational complexity.

Production recommendations:
- Enable etcd encryption at rest.
- Restrict secret access via RBAC least privilege.
- Do not store real secrets in Git/values files.
- Use Vault (or external secret manager) for sensitive credentials.
- Rotate credentials regularly and audit access.
