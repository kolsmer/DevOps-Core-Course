# Pulumi AWS Infrastructure

This directory contains Infrastructure as Code using Pulumi (Python) for Lab 4.

## Overview

Pulumi provides an **imperative** approach using real programming languages (Python). Compare with the **declarative** Terraform approach.

**Key Differences:**
- Terraform: HCL (domain-specific) + declarative
- Pulumi: Python (general-purpose) + imperative
- Both create same AWS infrastructure

## Prerequisites

1. **Pulumi CLI** - [Download](https://www.pulumi.com/docs/install/)
2. **AWS Account** with free tier
3. **AWS Credentials**: Access Key ID & Secret Access Key
4. **Python 3.9+** installed
5. **SSH public key** at `~/.ssh/id_rsa.pub`

## Setup

### 1. Install Pulumi

```bash
# macOS
brew install pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows - Download from pulumi.com/docs/install

pulumi version
```

### 2. Get AWS Credentials

1. [AWS Console](https://console.aws.amazon.com/) → IAM → Users
2. Create Access Key → Download CSV
3. Note:
   - Access Key ID
   - Secret Access Key

### 3. Set Environment Variables

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

Add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export AWS_ACCESS_KEY_ID="..."' >> ~/.bashrc
source ~/.bashrc
```

### 4. Create Python Virtual Environment

```bash
cd pulumi
python3 -m venv venv
source venv/bin/activate      # Linux/macOS
# or
venv\Scripts\activate          # Windows
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Initialize Pulumi Stack

```bash
# First time
pulumi login --local
pulumi stack init dev

# Or use existing
pulumi stack select dev
```

## Quick Start

### 1. Preview Infrastructure

```bash
pulumi preview
```

Shows resources to create:
- VPC (10.0.0.0/16)
- Subnet (10.0.1.0/24)
- Internet Gateway, Route Table
- Security Group (SSH, HTTP, HTTPS, port 5000)
- EC2 t2.micro (Ubuntu 22.04)
- SSH Key Pair

### 2. Create Infrastructure

```bash
pulumi up
```

Confirm when prompted. Takes 2-3 minutes.

### 3. View Outputs

```bash
pulumi stack output
```

Shows:
- `instance_public_ip`: Public IP
- `ssh_connection_string`: SSH command
- `http_url`: HTTP access
- `app_url`: App port (5000)

### 4. Connect to VM

```bash
ssh -i ~/.ssh/id_rsa ubuntu@<public-ip>
```

### 5. Destroy When Done

```bash
pulumi destroy
```

## Configuration

```bash
pulumi config set aws_region "us-east-1"
pulumi config set instance_name "lab04-pulumi-vm"
pulumi config   # View all config
```

## Useful Commands

```bash
# Stack management
pulumi stack list
pulumi stack select dev

# View outputs
pulumi stack output
pulumi stack output instance_public_ip

# Infrastructure
pulumi preview              # Plan
pulumi up                  # Apply
pulumi destroy             # Delete
pulumi refresh             # Sync state

# History
pulumi history
```

## Troubleshooting

### Error: "error importing default credentials"

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
echo $AWS_ACCESS_KEY_ID
```

### SSH public key not found

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

### VM not responding to SSH

Wait 2-3 minutes after `pulumi up` completes.

```bash
pulumi stack output instance_public_ip
ssh -i ~/.ssh/id_rsa ubuntu@$(pulumi stack output -raw instance_public_ip)
```

### Unexpected charges

Always destroy when done:
```bash
pulumi destroy
```

## Terraform vs Pulumi

| Aspect | Terraform | Pulumi |
|--------|-----------|--------|
| Language | HCL | Python |
| Style | Declarative | Imperative |
| Learning | Moderate | Gentle |
| Reuse | Modules | Functions |
| Testing | External | Native |

## Lab 5 Preparation

Your VM is ready for **Lab 5 (Ansible)**:
- Ubuntu 22.04 on AWS
- SSH key-based auth
- Docker installed
- HTTP/HTTPS ports open
- Port 5000 for apps

## AWS Free Tier

- t2.micro: 750 hours/month (12 months)
- 20 GB EBS
- 1 GB data transfer/month
- **Total: $0** if within limits

## Resources

- [Pulumi Docs](https://www.pulumi.com/docs/)
- [AWS Provider](https://www.pulumi.com/registry/packages/aws/)
- [Python SDK](https://www.pulumi.com/docs/languages-sdks/python/)
- [AWS Free Tier](https://aws.amazon.com/free/)

## Next Steps

1. Create infrastructure (`pulumi up`)
2. Verify SSH access
3. Compare with Terraform
4. Use for Lab 5 (Ansible)
