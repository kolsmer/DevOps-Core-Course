# Terraform Infrastructure

This directory contains Infrastructure as Code (IaC) using Terraform for Lab 4.

## Overview

We use Docker as a provider to create a simulated "infrastructure" on the local machine. This demonstrates Terraform concepts without requiring cloud credentials or actual VM provisioning.

## Directory Structure

```
terraform/
├── .gitignore           # Ignore Terraform state files
├── README.md            # This file
└── docker/              # Docker-based infrastructure
    ├── main.tf          # Main infrastructure definition
    ├── variables.tf     # Input variables
    ├── outputs.tf       # Output values
    └── terraform.tfvars # Variable values
```

## Prerequisites

- Terraform 1.9+
- Docker (running daemon)
- SSH key pair (~/.ssh/id_rsa.pub exists)

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform/docker
terraform init
```

### 2. Plan Infrastructure

```bash
terraform plan
```

This shows what resources will be created.

### 3. Apply Infrastructure

```bash
terraform apply
```

This creates the Docker container with SSH, HTTP, and port 5000 access.

### 4. Get Connection Details

```bash
terraform output -json
```

Example output:
```json
{
  "ssh_connection": "ssh -p 2222 root@localhost",
  "http_url": "http://localhost:8080",
  "app_url": "http://localhost:5000"
}
```

### 5. Connect via SSH

```bash
ssh -p 2222 root@localhost
```

### 6. Destroy Infrastructure

```bash
terraform destroy
```

## What Gets Created

1. **Docker Network** (`devops-net`)
   - Bridge network for container communication
   - IP: 172.20.0.0/16

2. **Docker Container** (`devops-vm`)
   - Base image: Ubuntu 22.04
   - SSH server running (port 2222 external)
   - HTTP server available (port 8080 external)
   - Application port (port 5000 external)
   - Root SSH access configured

## Configuration

Edit `terraform/docker/terraform.tfvars` to customize:

```hcl
ssh_port       = 2222     # External SSH port
http_port      = 8080     # External HTTP port
app_port       = 5000     # External app port
container_name = "devops-vm"  # Container name
```

## Terraform Files

### main.tf
- Defines providers (Docker, null)
- Creates Docker network
- Creates Docker container
- Sets up SSH access

### variables.tf
- Declares all input variables
- Provides descriptions and defaults

### outputs.tf
- Exports connection strings
- Exports container info for Lab 5+ usage

### terraform.tfvars
- Sets variable values
- Override here without modifying code

## Best Practices Demonstrated

1. **Provider Configuration**: Docker provider setup
2. **Variables**: Reusable configuration parameters
3. **Outputs**: Exporting important values for consumption
4. **Locals**: Computing derived values (SSH public key)
5. **Provisioners**: Running local commands for setup
6. **Labels**: Resource tagging for management
7. **State Management**: Terraform state tracking (ignore in Git)
8. **Dependencies**: Explicit depends_on for setup ordering

## Troubleshooting

### Docker daemon not running
```bash
sudo systemctl start docker
```

### SSH key not found
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

### Permission denied connecting
```bash
# Check if password auth is available (fallback)
ssh -p 2222 root@localhost  # Try if set up pwd
```

### State file conflicts
```bash
rm -rf .terraform terraform.tfstate*
terraform init
```

## Next Steps for Lab 5

After successfully applying this Terraform configuration:
1. Note the SSH connection string from outputs
2. Verify SSH access works
3. In Lab 5 (Ansible), use this connection for provisioning

## For Lab 4 Bonus: CI/CD for Infrastructure

See `.github/workflows/terraform-ci.yml` for automated Terraform validation and planning.