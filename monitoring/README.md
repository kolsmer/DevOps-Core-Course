# Monitoring Stack

Centralized logs + metrics with Loki, Promtail, Prometheus, and Grafana.

## Quick Start

```bash
cp .env.example .env        # set GF_ADMIN_PASSWORD
docker compose up -d
```

| Service  | URL                          |
|----------|------------------------------|
| Grafana  | <http://localhost:3000>       |
| Prometheus | <http://localhost:9090>     |
| Loki     | <http://localhost:3100/ready> |
| Promtail | <http://localhost:9080/targets> |

Grafana datasources (Loki + Prometheus) and dashboards are provisioned automatically.

## Stack

| Component | Image | Role |
|-----------|-------|------|
| Loki | `grafana/loki:3.0.0` | Log storage |
| Promtail | `grafana/promtail:3.0.0` | Log collector |
| Prometheus | `prom/prometheus:v3.9.0` | Metrics scrape + TSDB |
| Grafana | `grafana/grafana:12.3.1` | Dashboards |
| app-python | built from `../app_python` | Monitored app |

## Log Collection

Only containers with label `logging=promtail` are scraped by Promtail.  
The Python app emits structured JSON logs automatically.

## Ansible Deployment

```bash
cd ansible
ansible-playbook playbooks/deploy-monitoring.yml --tags monitoring
```
