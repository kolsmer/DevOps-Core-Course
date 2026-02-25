# LAB05 — Ansible Fundamentals

## Student / Environment
- Repository: `DevOps-Core-Course`
- Target host: `lab04-vm (93.77.186.203)`
- Control node OS: Linux
- Python venv: `/home/ramil/Work/DevOps-Core-Course/.venv`

## Goal
Build role-based Ansible automation for:
1. Base VM provisioning (`common`, `docker`)
2. App deployment (`app_deploy`) with secrets in Ansible Vault
3. Idempotent execution

## 1. Architecture Overview
- Ansible version: `ansible-core 2.20.3`.
- Target VM: `lab04-vm`, OS/version: `Ubuntu 22.04.5 LTS` (`PRETTY_NAME` from `/etc/os-release`).
- Role-based structure is used (`common` -> `docker` -> `app_deploy`) to separate provisioning logic from deployment logic.
- Roles are chosen over one monolithic playbook to keep responsibilities isolated, enable reuse in future labs, and simplify testing/troubleshooting.

## Implemented Structure

```text
ansible/
├── ansible.cfg
├── inventory/hosts.ini
├── group_vars/all.yml               # encrypted via ansible-vault
├── playbooks/
│   ├── provision.yml
│   ├── deploy.yml
│   └── site.yml
├── roles/
│   ├── common/
│   │   ├── defaults/main.yml
│   │   └── tasks/main.yml
│   ├── docker/
│   │   ├── defaults/main.yml
│   │   ├── handlers/main.yml
│   │   └── tasks/main.yml
│   └── app_deploy/
│       ├── defaults/main.yml
│       ├── handlers/main.yml
│       └── tasks/main.yml
└── docs/LAB05.md
```

## Roles

### 1) `common`
- **Purpose:** Base OS preparation for all hosts (apt cache, essential utilities, timezone).
- **Variables:** `common_packages` (list of base packages), `common_timezone` (`UTC` by default).
- **Handlers:** none.
- **Dependencies:** none.

### 2) `docker`
- **Purpose:** Install and configure Docker Engine and runtime prerequisites on Ubuntu hosts.
- **Variables:** `docker_user` (defaults to `ansible_user`), `docker_packages`, `docker_repo`.
- **Handlers:** `restart docker` (service restart handler defined in role).
- **Dependencies:** assumes `common` role has already prepared baseline packages and system state.

### 3) `app_deploy`
- **Purpose:** Authenticate to Docker Hub, pull app image, run container, and verify health.
- **Variables:** `dockerhub_username`, `dockerhub_password` (Vault), `docker_image`, `docker_image_tag`, `app_port`, `app_container_port`, `app_container_name`, `app_restart_policy`, `app_healthcheck_path`, `app_environment`.
- **Handlers:** `restart app container` (uses `community.docker.docker_container` with `restart: true`).
- **Dependencies:** requires Docker runtime from `docker` role and valid Vault credentials.

## Playbooks

### `playbooks/provision.yml`
Runs roles:
- `common`
- `docker`

### `playbooks/deploy.yml`
- Loads encrypted vars: `../group_vars/all.yml`
- Runs role: `app_deploy`

### `playbooks/site.yml`
- Full flow: provisioning + deployment

## Ansible Vault

### Encrypted variables file
Created and encrypted:
```bash
ansible-vault encrypt group_vars/all.yml.plain --output group_vars/all.yml --vault-password-file .vault_pass
```

### Vault password strategy
- `ansible/.vault_pass` used for local execution
- Added to `.gitignore`
- `ansible.cfg` includes `vault_password_file = .vault_pass`

### Security note
`group_vars/all.yml` is encrypted and safe to commit.
Vault password file is NOT committed.

### Encrypted file example
`group_vars/all.yml` begins with Vault header, confirming encryption:
```text
$ANSIBLE_VAULT;1.1;AES256
```

Why Ansible Vault is important: it allows committing infrastructure code with secrets protected at rest, preventing plaintext credential leaks in Git history and reviews.

## Validation and Execution

### Tool versions
```bash
ansible [core 2.20.3]
python version = 3.12.3
community.docker 5.0.6
```

### Syntax checks
```bash
ansible-playbook playbooks/provision.yml --syntax-check
ansible-playbook playbooks/deploy.yml --syntax-check --vault-password-file .vault_pass
ansible-playbook playbooks/site.yml --syntax-check --vault-password-file .vault_pass
```
Result: all passed.

### Connectivity checks
```bash
ansible all -m ping
```
Result:
```text
lab04-vm | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Provision run #1
```bash
ansible-playbook playbooks/provision.yml
```
Result summary:
```text

PLAY [Provision web servers] ********************************************************************

TASK [Gathering Facts] **************************************************************************
ok: [lab04-vm]

TASK [common : Update apt cache] ****************************************************************
ok: [lab04-vm]

TASK [common : Install common packages] *********************************************************
ok: [lab04-vm]

TASK [common : Check current timezone] **********************************************************
ok: [lab04-vm]

TASK [common : Set timezone] ********************************************************************
skipping: [lab04-vm]

TASK [docker : Install Docker prerequisites] ****************************************************
ok: [lab04-vm]

TASK [docker : Ensure keyrings directory exists] ************************************************
ok: [lab04-vm]

TASK [docker : Add Docker GPG key] **************************************************************
ok: [lab04-vm]

TASK [docker : Add Docker repository] ***********************************************************
ok: [lab04-vm]

TASK [docker : Install Docker packages] *********************************************************
ok: [lab04-vm]

TASK [docker : Ensure docker socket is enabled and running] *************************************
changed: [lab04-vm]

TASK [docker : Ensure Docker service is enabled and running] ************************************
changed: [lab04-vm]

TASK [docker : Add user to docker group] ********************************************************
ok: [lab04-vm]

TASK [docker : Install Python Docker SDK package] ***********************************************
changed: [lab04-vm]

PLAY RECAP **************************************************************************************
lab04-vm                   : ok=13   changed=3    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   

```
Analysis (what changed and why):
- `docker : Ensure docker socket is enabled and running` changed because socket activation had to be enabled on the VM.
- `docker : Ensure Docker service is enabled and running` changed because Docker service state converged to `started/enabled`.
- `docker : Install Python Docker SDK package` changed because `python3-docker` was installed for Ansible Docker modules.

### Provision run #2 (Idempotency)
```bash
ansible-playbook playbooks/provision.yml
```
Result summary:
```text
PLAY [Provision web servers] ********************************************************************

TASK [Gathering Facts] **************************************************************************
ok: [lab04-vm]

TASK [common : Update apt cache] ****************************************************************
ok: [lab04-vm]

TASK [common : Install common packages] *********************************************************
ok: [lab04-vm]

TASK [common : Check current timezone] **********************************************************
ok: [lab04-vm]

TASK [common : Set timezone] ********************************************************************
skipping: [lab04-vm]

TASK [docker : Install Docker prerequisites] ****************************************************
ok: [lab04-vm]

TASK [docker : Ensure keyrings directory exists] ************************************************
ok: [lab04-vm]

TASK [docker : Add Docker GPG key] **************************************************************
ok: [lab04-vm]

TASK [docker : Add Docker repository] ***********************************************************
ok: [lab04-vm]

TASK [docker : Install Docker packages] *********************************************************
ok: [lab04-vm]

TASK [docker : Ensure docker socket is enabled and running] *************************************
ok: [lab04-vm]

TASK [docker : Ensure Docker service is enabled and running] ************************************
ok: [lab04-vm]

TASK [docker : Add user to docker group] ********************************************************
ok: [lab04-vm]

TASK [docker : Install Python Docker SDK package] ***********************************************
ok: [lab04-vm]

PLAY RECAP **************************************************************************************
lab04-vm                   : ok=13   changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
```
This confirms idempotency: second run made no changes.
Explanation: all provisioning tasks use state-driven modules (`apt`, `service`, `user`) and converge to desired state, so re-run produces `changed=0`.

### Deploy run
```bash
ansible-playbook playbooks/deploy.yml
```
Result summary:
```text
PLAY [Deploy application] ***********************************************************************

TASK [Gathering Facts] **************************************************************************
ok: [lab04-vm]

TASK [app_deploy : Log in to Docker Hub] ********************************************************
changed: [lab04-vm]

TASK [app_deploy : Pull application image] ******************************************************
changed: [lab04-vm]

TASK [app_deploy : Stop existing container] *****************************************************
ok: [lab04-vm]

TASK [app_deploy : Remove existing container] ***************************************************
ok: [lab04-vm]

TASK [app_deploy : Run application container] ***************************************************
changed: [lab04-vm]

TASK [app_deploy : Wait for application port] ***************************************************
ok: [lab04-vm]

TASK [app_deploy : Verify health endpoint] ******************************************************
ok: [lab04-vm]

RUNNING HANDLER [app_deploy : restart app container] ********************************************
changed: [lab04-vm]

PLAY RECAP **************************************************************************************
lab04-vm                   : ok=9    changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

Handler execution:
```text
RUNNING HANDLER [app_deploy : restart app container]
changed: [lab04-vm]
```

Notes:
- Deployment role currently recreates container each run (`stop -> remove -> run`), so repeated deploy runs are not fully idempotent by design.
- Provisioning playbook remains idempotent (`changed=0` on second run).

### Runtime verification
Container status:
```bash
ansible webservers -a "docker ps"
```

Output excerpt:
```text
CONTAINER ID   IMAGE                       COMMAND           STATUS          PORTS                    NAMES
...            kolsmer/devops-app:latest   "python app.py"   Up ...          0.0.0.0:5000->8000/tcp   devops-app
```

Health endpoint check:
```bash
ansible webservers -a "curl -sS http://127.0.0.1:5000/health"
```

Output:
```json
{"status":"healthy","timestamp":"2026-02-25T11:37:06.253360+00:00Z","uptime_seconds":26}
```

## Conclusions
- Role-based Ansible structure implemented fully.
- Provisioning pipeline is stable and idempotent.
- Vault integration is configured and working.
- Application deployment completed successfully on `lab04-vm`.

## 6. Key Decisions

### Why use roles instead of plain playbooks?
Roles provide a clean separation of concerns and standard structure (`tasks/defaults/handlers`) so the automation is easier to navigate and review. This reduces coupling and makes each part of the system independently maintainable.

### How do roles improve reusability?
Each role encapsulates one responsibility and can be reused across environments or future labs with different variables. The same `docker` or `common` role can be applied to multiple hosts without duplicating task definitions.

### What makes a task idempotent?
A task is idempotent when repeated execution converges to the same desired state without extra changes. Using declarative modules (`apt state=present`, `service state=started`, conditional timezone change) ensures safe re-runs.

### How do handlers improve efficiency?
Handlers run only when notified by a changed task, so expensive operations (service/container restart) are skipped when no configuration drift occurred. This reduces unnecessary restarts and speeds up repeated runs.

### Why is Ansible Vault necessary?
Vault keeps sensitive data encrypted while allowing the encrypted file to stay in version control. This is essential for team workflows where infrastructure code is shared but secrets must remain protected.
