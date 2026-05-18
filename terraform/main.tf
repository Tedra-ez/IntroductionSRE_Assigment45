terraform {
  required_version = ">= 1.5.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

# Local/demo provisioning: generates inventory for Ansible.
# For cloud VMs, replace with aws/google/azurerm provider blocks.

variable "project_name" {
  type    = string
  default = "sre-microservices"
}

variable "node_count" {
  type    = number
  default = 2
}

variable "ssh_user" {
  type    = string
  default = "ubuntu"
}

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory/hosts.ini"
  content  = templatefile("${path.module}/templates/inventory.tpl", {
    nodes = [for i in range(var.node_count) : {
      name = "sre-node-${i + 1}"
      ip   = "192.168.56.1${i + 0}"
    }]
    ssh_user = var.ssh_user
  })
}

output "inventory_path" {
  value = local_file.ansible_inventory.filename
}

output "project_name" {
  value = var.project_name
}
