# Lab 3 - CI/CD (Python)

## Overview
- **Testing framework:** pytest (simple syntax, fast, good FastAPI support).
- **What is tested:** `/`, `/health`, and 404 handler.
- **CI goal:** run lint + tests on every change; build/push Docker image on main only.
- **Versioning:** CalVer (YYYY.MM.DD) + latest.

## Local Testing
```bash
cd app_python
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## CI Workflow
- **Workflow:** `.github/workflows/python-ci.yml`
- **Triggers:** push/PR only when `app_python/**` changes.
- **Jobs:**
  - **Test job:** ruff lint + pytest (matrix: 3.12, 3.13)
  - **Docker job:** build + push (only on main/master)

## Docker Tags (CalVer)
- `kolsmer/devops-app:YYYY.MM.DD`
- `kolsmer/devops-app:YYYY.MM`
- `kolsmer/devops-app:latest`

## Best Practices Applied
- **Matrix testing:** catches version-specific issues.
- **Dependency caching:** faster runs via `setup-python` pip cache.
- **Job dependency:** Docker push only if tests pass.
- **Concurrency:** cancels outdated runs.
- **Secrets:** Docker Hub and Snyk tokens stored in GitHub Secrets.

## Security Scan (Snyk)
- Action: `snyk/actions/python@v3.1.0`
- Threshold: `high`
- Requires `SNYK_TOKEN` secret.

## Required Secrets
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `SNYK_TOKEN` (optional but recommended)

## Evidence
- **Workflow run:** <paste Actions link>
- **Docker Hub:** https://hub.docker.com/r/kolsmer/devops-app
- **Docker Hub tags:** `latest`, `1.0` (see docker-tags screenshot)
- **Tests output:**
```
================================== test session starts ===================================
platform linux -- Python 3.12.3, pytest-8.3.4, pluggy-1.6.0
rootdir: /home/ramil/Work/DevOps-Core-Course/app_python
plugins: cov-5.0.0, anyio-4.12.1
collected 3 items

tests/test_app.py ...                                                              [100%]

=================================== 3 passed in 0.37s ====================================
```
