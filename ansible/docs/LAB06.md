# LAB06 — Advanced Ansible & CI/CD

## 1. Environment
- Control node: Linux
- Ansible: `core 2.20.3`
- Target host: `lab04-vm` (`Ubuntu 22.04.5 LTS`)
- Docker modules: `community.docker`

## 2. What was implemented

### 2.1 Refactor with Blocks & Tags

#### `roles/common/tasks/main.yml`
Implemented blocks and tags:
- `packages` block: apt cache update, package installation, timezone check/set
- `users` block: managed users loop (`common_users`)
- `rescue`: fallback with `apt-get update --fix-missing` and retry install
- `always`: writes completion log into `/tmp/ansible-common.log`
- role tags used: `common`, `packages`, `users`

#### `roles/docker/tasks/main.yml`
Implemented blocks and tags:
- `docker_install` block: prerequisites, keyring, GPG key, repo, package install
- `docker_config` block: socket, group membership, python docker sdk
- `rescue`: wait + apt refresh + retry key/repo/packages
- `always`: ensure `docker` service is enabled and started
- role tags used: `docker`, `docker_install`, `docker_config`

#### Tag discovery result
Command:
```bash
ansible-playbook playbooks/provision.yml --list-tags
```
Output:
```text
TASK TAGS: [common, docker, docker_config, docker_install, packages, users]
```

#### Selective execution evidence
Only Docker install tasks:
```bash
ansible-playbook playbooks/provision.yml --tags docker_install
```
Result recap:
```text
lab04-vm : ok=6 changed=0 failed=0
```

Skip common role:
```bash
ansible-playbook playbooks/provision.yml --skip-tags common
```
Result recap:
```text
lab04-vm : ok=10 changed=0 failed=0
```

Check mode for docker tags:
```bash
ansible-playbook playbooks/provision.yml --tags docker --check
```
Result recap:
```text
lab04-vm : ok=10 changed=1 failed=0
```

### 2.2 Upgrade to Docker Compose and role dependency

Replaced `app_deploy` with `web_app` role:
- `roles/web_app/defaults/main.yml`
- `roles/web_app/tasks/main.yml`
- `roles/web_app/tasks/wipe.yml`
- `roles/web_app/handlers/main.yml`
- `roles/web_app/meta/main.yml`
- `roles/web_app/templates/docker-compose.yml.j2`

Key changes:
- Deployment is done by `community.docker.docker_compose_v2`
- Compose file rendered from template to `{{ compose_project_dir }}/docker-compose.yml`
- Role dependency configured in `meta/main.yml`:
  - `web_app` depends on `docker`
- Migration guard added: legacy standalone container is removed before compose deployment if it has no compose labels

### 2.3 Playbooks and tagging
Updated playbooks to role+tag format:
- `playbooks/provision.yml`
- `playbooks/deploy.yml`
- `playbooks/site.yml`

`deploy.yml` now uses role `web_app` with tags:
- `web_app`
- `app_deploy` (backward-friendly alias)
- `compose`

### 2.4 Wipe logic (double-gating)
Implemented in `roles/web_app/tasks/wipe.yml` and role flow:
- Wipe executes only when BOTH conditions are true:
  1. `web_app_wipe=true`
  2. run includes `--tags web_app_wipe`
- Safety condition:
```yaml
when:
  - web_app_wipe | bool
  - "'web_app_wipe' in ansible_run_tags"
```

#### Wipe behavior matrix (validated)

Scenario 1 — `web_app_wipe=false` + `--tags web_app_wipe`:
- Wipe tasks skipped
- Container count after run (`docker ps | grep -c devops-app`): `1`

Scenario 2 — `web_app_wipe=true` without wipe tag:
- Wipe tasks skipped
- Container count after run: `1`

Scenario 3 — `web_app_wipe=true` + `--tags web_app_wipe`:
- Wipe executed (`stop/remove stack`, remove compose file/dir)
- Container count after run: `0`

Scenario 4 — redeploy, then `web_app_wipe=false` + `--tags web_app_wipe`:
- Wipe skipped
- Container count after run: `1`
- Health check returns `healthy`

## 3. CI/CD integration

Added workflow:
- `.github/workflows/ansible-deploy.yml`

Pipeline stages:
1. `lint` job:
   - install `ansible-core`, `ansible-lint`, `community.docker`
   - run `ansible-lint playbooks/*.yml`
2. `deploy` job (on push):
   - creates temporary inventory from GitHub Secrets
   - runs `ansible-playbook playbooks/deploy.yml`
   - verifies `http://<VM_HOST>:5000/health`

Required GitHub Secrets:
- `SSH_PRIVATE_KEY`
- `VM_HOST`
- `VM_USER`
- `ANSIBLE_VAULT_PASSWORD`

Added workflow badge in root `README.md`.

## 4. Runtime verification

Successful deploy recap:
```text
PLAY RECAP
lab04-vm : ok=19 changed=3 failed=0
```

Container check:
```bash
ansible webservers -a "docker ps"
```
Shows running container based on `kolsmer/devops-app:latest` and published port `5000->8000`.

Health check:
```bash
ansible webservers -a "curl -sS http://127.0.0.1:5000/health"
```
Output example:
```json
{"status":"healthy","timestamp":"2026-03-03T10:26:41.334344+00:00Z","uptime_seconds":88}
```

## 5. Validation summary
- `ansible-playbook playbooks/provision.yml --syntax-check` 
- `ansible-playbook playbooks/deploy.yml --syntax-check` 
- `ansible-playbook playbooks/site.yml --syntax-check` 
- tags behavior validated (`--list-tags`, `--tags`, `--skip-tags`, `--check`) 
- wipe double-gating validated with 4 scenarios 

Evidence status:
- Selective tag execution evidence: provided
- Wipe scenarios evidence (all 4): provided
- Docker Compose deployment and health evidence: provided
- CI workflow file and badge: provided
- Rescue-trigger runtime output: captured via dedicated demo playbook run (see below)
- GitHub Actions successful run screenshots/log excerpts: pending in GitHub UI after push

### Rescue block evidence (runtime)
Command:
```bash
ansible-playbook playbooks/rescue_demo.yml
```

Output excerpt:
```text
TASK [Force failure] ... FAILED!
TASK [Rescue executed]
ok: [lab04-vm] => {
  "msg": "rescue block executed"
}

PLAY RECAP
lab04-vm : ok=1 changed=0 failed=0 rescued=1
```

## 6. Research questions (short answers)

### What happens if rescue block also fails?
Play execution fails for that host after rescue is exhausted, and Ansible reports task failure in recap. `always` section still runs regardless of success/failure.

### Can blocks be nested?
Yes, blocks can be nested, but readability drops quickly. In practice it is better to keep one clear block level and split complex flows into included task files.

### How do tags inherit inside blocks?
Tags applied on a block are inherited by tasks in that block. Individual tasks can also have additional tags.

## 6.2 Task 2 research answers

### What is the difference between restart: always and restart: unless-stopped?
`always` restarts container after any stop (including manual stop after daemon restart), while `unless-stopped` keeps the container stopped if it was manually stopped. For service-like apps, `unless-stopped` is usually safer during maintenance.

### How do Docker Compose networks differ from Docker bridge networks?
Compose creates project-scoped bridge networks automatically and attaches services with predictable DNS names based on service names. Plain bridge usage is manual and does not provide the same service-centric naming and lifecycle coupling.

### Can Ansible Vault variables be used in templates?
Yes. Vaulted variables are decrypted at runtime and can be used in Jinja2 templates exactly like regular variables, as long as playbook execution has vault access.

### community.docker.docker_compose_v2: state present vs alternatives
`state: present` ensures stack services exist and are running according to compose file. `state: absent` removes stack resources; with `pull` and `recreate` options you can fine-tune update behavior.

## 6.3 Task 3 research answers

### Why use both variable and tag for wipe?
This is double safety: configuration intent (`web_app_wipe=true`) plus explicit operator action (`--tags web_app_wipe`). It prevents accidental destructive actions from a single mistake.

### Difference between never tag and this approach
`never` is tag-only gating and does not express runtime intent through variables. Variable + tag gating is clearer, auditable in play invocation, and easier to combine with conditional logic.

### Why must wipe come before deployment in main tasks?
It supports clean reinstall flow in one run: remove old state first, then deploy fresh state. If reversed, old artifacts may conflict with new deployment.

### When clean reinstall is better than rolling update
Clean reinstall is useful when state drift is large, compose structure changed significantly, or rollback cleanup is required. Rolling updates are preferable for minimal disruption when changes are small and backward-compatible.

### How to extend wipe to images and volumes
Add optional tasks guarded by dedicated flags (for example `web_app_wipe_images`, `web_app_wipe_volumes`) and remove only project-scoped resources. Keep them behind additional tags to avoid over-deletion.

## 6.4 Task 4 research answers

### Security implications of storing SSH keys in GitHub Secrets
Secrets reduce plaintext exposure in repo, but compromise risk remains if workflow is abused or logs leak sensitive data. Least privilege keys, environment protection, and masked outputs are required.

### How to implement staging -> production pipeline
Use separate jobs/environments with required approvals: deploy to staging first, run smoke/integration checks, then promote to production. Keep separate inventory, vault password, and host secrets per environment.

### What to add for rollback support
Track immutable image tags, keep previous tag in deployment metadata, and add rollback playbook/job to redeploy last known good version. Persist release history in artifacts or Git tags.

### How self-hosted runner can improve security vs GitHub-hosted
Self-hosted runner can stay inside private network, reducing SSH exposure and public ingress. It also allows stricter network controls, but requires hardening and lifecycle management by the team.

## 7. Challenges and solutions
- Docker daemon start issue due to socket activation path: fixed by ensuring `docker.socket` is started before Docker service convergence.
- Compose migration from legacy standalone container: added compose-label detection and one-time removal of non-compose container.
- Wipe safety ambiguity: implemented strict double-gating and validated behavior matrix with 4 scenarios.
- Ad-hoc command templating conflict with docker format braces: switched runtime checks to shell-safe commands for evidence capture.

## 8. Conclusion
Lab 6 upgrades are complete: blocks/tags/rescue/always, Docker Compose deployment, role dependencies, safe wipe logic with strict double-gating, and CI/CD automation with GitHub Actions.
