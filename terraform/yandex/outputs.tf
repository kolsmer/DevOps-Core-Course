output "vm_id" {
  description = "ID of the created VM instance"
  value       = yandex_compute_instance.web_vm.id
}

output "vm_name" {
  description = "Name of the created VM"
  value       = yandex_compute_instance.web_vm.name
}

output "internal_ip" {
  description = "Internal IP address of the VM"
  value       = yandex_compute_instance.web_vm.network_interface[0].ip_address
}

output "external_ip" {
  description = "External (public) IP address of the VM"
  value       = yandex_compute_instance.web_vm.network_interface[0].nat_ip_address
}

output "ssh_connection_string" {
  description = "SSH command to connect to the VM"
  value       = "ssh -i /home/ramil/.ssh/id_ed25519 ubuntu@${yandex_compute_instance.web_vm.network_interface[0].nat_ip_address}"
}

output "http_url" {
  description = "HTTP URL to access the VM"
  value       = "http://${yandex_compute_instance.web_vm.network_interface[0].nat_ip_address}"
}

output "app_url" {
  description = "Application port URL"
  value       = "http://${yandex_compute_instance.web_vm.network_interface[0].nat_ip_address}:${var.app_port}"
}

output "network_id" {
  description = "ID of the VPC network"
  value       = yandex_vpc_network.lab_network.id
}

output "subnet_id" {
  description = "ID of the subnet"
  value       = yandex_vpc_subnet.lab_subnet.id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = yandex_vpc_security_group.lab_sg.id
}

output "instance_labels" {
  description = "Labels applied to the instance"
  value       = yandex_compute_instance.web_vm.labels
}
