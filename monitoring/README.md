# Monitoring — Loki Stack

Centralized logging with **Loki 3.0**, **Promtail 3.0**, and **Grafana 12.3**.

## Quick Start

```bash
cp .env.example .env        # set GF_ADMIN_PASSWORD
docker compose up -d
```

| Service  | URL                          |
|----------|------------------------------|
| Grafana  | <http://localhost:3000>       |
| Loki     | <http://localhost:3100/ready> |
| Promtail | <http://localhost:9080/targets> |

Loki datasource and the **App Logs Dashboard** are provisioned automatically.

## Stack

| Component | Image              | Role                     |
|-----------|--------------------|--------------------------|
| Loki      | `grafana/loki:3.0.0`     | Log storage (TSDB)       |
| Promtail  | `grafana/promtail:3.0.0` | Log collector (Docker SD)|
| Grafana   | `grafana/grafana:12.3.1` | Visualization            |
| app-python | built from `../app_python` | App under observation |

## Log Collection

Only containers with label `logging=promtail` are scraped by Promtail.  
The Python app emits structured JSON logs automatically.

## Ansible Deployment

```bash
cd ansible
ansible-playbook playbooks/deploy-monitoring.yml --tags monitoring
```
