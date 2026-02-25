variable "service_account_key_file" {
  description = "Path to the Yandex Cloud service account key file (JSON)"
  type        = string
  sensitive   = true
}

variable "cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
  sensitive   = true
}

variable "folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
  sensitive   = true
}

variable "zone" {
  description = "Availability zone in Yandex Cloud"
  type        = string
  default     = "ru-central1-a"
}

variable "network_name" {
  description = "Name of the VPC network"
  type        = string
  default     = "lab04-network"
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_name" {
  description = "Name of the compute instance (VM)"
  type        = string
  default     = "lab04-vm"
}

variable "instance_hostname" {
  description = "Hostname for the VM"
  type        = string
  default     = "lab04-vm"
}

variable "platform_id" {
  description = "Platform type for the VM"
  type        = string
  default     = "standard-v3"
}

variable "cpu_cores" {
  description = "Number of CPU cores"
  type        = number
  default     = 2
}

variable "cpu_fraction" {
  description = "Guaranteed share of CPU (20% for free tier)"
  type        = number
  default     = 20
}

variable "memory_gb" {
  description = "Amount of RAM in GB"
  type        = number
  default     = 1
}

variable "boot_disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 10
}

variable "ssh_port" {
  description = "SSH port number"
  type        = number
  default     = 22
}

variable "http_port" {
  description = "HTTP port number"
  type        = number
  default     = 80
}

variable "app_port" {
  description = "Application port number"
  type        = number
  default     = 5000
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key file for root access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
