terraform {
  required_version = ">= 1.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = ">= 0.99"
    }
  }
}

provider "yandex" {
  service_account_key_file = var.service_account_key_file
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
  zone                     = var.zone
}

# Get latest Ubuntu 22.04 image
data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

# Create VPC network
resource "yandex_vpc_network" "lab_network" {
  name           = var.network_name
  description    = "Network for Lab 4 infrastructure"
}

# Create subnet within the network
resource "yandex_vpc_subnet" "lab_subnet" {
  name           = "${var.network_name}-subnet"
  description    = "Subnet for Lab 4"
  v4_cidr_blocks = [var.subnet_cidr]
  network_id     = yandex_vpc_network.lab_network.id
  zone           = var.zone
}

# Create security group
resource "yandex_vpc_security_group" "lab_sg" {
  name       = "${var.instance_name}-sg"
  network_id = yandex_vpc_network.lab_network.id

  # SSH access
  ingress {
    protocol       = "TCP"
    port           = var.ssh_port
    v4_cidr_blocks = var.allowed_ssh_cidrs
    description    = "SSH access"
  }

  # HTTP access
  ingress {
    protocol       = "TCP"
    port           = var.http_port
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "HTTP access"
  }

  # App port (5000)
  ingress {
    protocol       = "TCP"
    port           = var.app_port
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Application port"
  }

  # Allow all outbound traffic
  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Allow all outbound"
  }
}

# Create compute instance (VM)
resource "yandex_compute_instance" "web_vm" {
  name        = var.instance_name
  hostname    = var.instance_hostname
  zone        = var.zone
  platform_id = var.platform_id

  resources {
    cores         = var.cpu_cores
    memory        = var.memory_gb
    core_fraction = var.cpu_fraction
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = var.boot_disk_size
    }
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.lab_subnet.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.lab_sg.id]
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.ssh_public_key_path)}"
    user-data = base64encode(templatefile("${path.module}/user_data.sh", {
      ssh_public_key = file(var.ssh_public_key_path)
    }))
  }

  labels = {
    lab      = "lab04"
    env      = "learning"
    tool     = "terraform"
    purpose  = "devops-course"
  }

  depends_on = [
    yandex_vpc_network.lab_network,
    yandex_vpc_subnet.lab_subnet,
  ]
}
