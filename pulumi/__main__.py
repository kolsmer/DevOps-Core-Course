import os
import pulumi
import pulumi_yandex as yandex

config = pulumi.Config()

cloud_id = config.require("cloud_id")
folder_id = config.require("folder_id")
service_account_key_file = config.require("service_account_key_file")

zone = config.get("zone") or "ru-central1-a"
instance_name = config.get("instance_name") or "lab04-pulumi-vm"
network_name = config.get("network_name") or "lab04-network"
security_group_name = config.get("security_group_name") or "lab04-vm-sg"
ssh_public_key_path = config.get("ssh_public_key_path") or "/home/ramil/.ssh/id_ed25519.pub"
ssh_public_key_path = os.path.expanduser(ssh_public_key_path)

with open(ssh_public_key_path, "r") as key_file:
    ssh_public_key = key_file.read().strip()

provider = yandex.Provider(
    "yc",
    service_account_key_file=service_account_key_file,
    cloud_id=cloud_id,
    folder_id=folder_id,
    zone=zone,
)

ubuntu_image = yandex.get_compute_image(
    family="ubuntu-2204-lts",
    opts=pulumi.InvokeOptions(provider=provider),
)

existing_network = yandex.get_vpc_network(
    name=network_name,
    opts=pulumi.InvokeOptions(provider=provider),
)

existing_subnet = yandex.get_vpc_subnet(
    name=f"{network_name}-subnet",
    opts=pulumi.InvokeOptions(provider=provider),
)

existing_security_group = yandex.get_vpc_security_group(
    name=security_group_name,
    opts=pulumi.InvokeOptions(provider=provider),
)

user_data_script = """#!/bin/bash
set -e
apt-get update
apt-get upgrade -y
apt-get install -y curl wget git build-essential python3 python3-pip docker.io
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu
apt-get install -y openssh-server openssh-client
systemctl start ssh
systemctl enable ssh
echo "Lab 4 VM initialization completed"
"""

instance = yandex.ComputeInstance(
    "web-vm",
    name=instance_name,
    hostname=instance_name,
    platform_id="standard-v3",
    resources=yandex.ComputeInstanceResourcesArgs(
        cores=2,
        memory=1,
        core_fraction=20,
    ),
    boot_disk=yandex.ComputeInstanceBootDiskArgs(
        initialize_params=yandex.ComputeInstanceBootDiskInitializeParamsArgs(
            image_id=ubuntu_image.id,
            size=10,
            type="network-hdd",
        )
    ),
    network_interfaces=[
        yandex.ComputeInstanceNetworkInterfaceArgs(
            subnet_id=existing_subnet.id,
            nat=True,
            security_group_ids=[existing_security_group.id],
        )
    ],
    metadata={
        "ssh-keys": f"ubuntu:{ssh_public_key}",
        "user-data": user_data_script,
    },
    labels={
        "env": "learning",
        "lab": "lab04",
        "purpose": "devops-course",
        "tool": "pulumi",
    },
    opts=pulumi.ResourceOptions(provider=provider),
)

pulumi.export("vm_id", instance.id)
pulumi.export("vm_name", instance.name)
pulumi.export("internal_ip", instance.network_interfaces[0].ip_address)
pulumi.export("external_ip", instance.network_interfaces[0].nat_ip_address)
pulumi.export(
    "ssh_connection_string",
    pulumi.Output.concat("ssh -i /home/ramil/.ssh/id_ed25519 ubuntu@", instance.network_interfaces[0].nat_ip_address),
)
pulumi.export(
    "http_url",
    pulumi.Output.concat("http://", instance.network_interfaces[0].nat_ip_address),
)
pulumi.export(
    "app_url",
    pulumi.Output.concat("http://", instance.network_interfaces[0].nat_ip_address, ":5000"),
)
pulumi.export("network_id", existing_network.id)
pulumi.export("subnet_id", existing_subnet.id)
pulumi.export("security_group_id", existing_security_group.id)
