terraform {
  required_version = ">= 1.5.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

terraform {
  required_version = ">= 1.5.0"
}

locals {
  generated_dir = "${path.root}/../generated"
}

resource "local_file" "k8s_values" {
  filename = "${local.generated_dir}/k8s-values.json"

  content = jsonencode({
    app_version = var.app_version
    namespace   = var.namespace
    app_port    = var.app_port
    db = {
      host     = var.db_host
      port     = var.db_port
      name     = var.db_name
      user     = var.db_user
      password = var.db_password
    }
  })
}

resource "local_file" "inventory" {
  filename = "${local.generated_dir}/inventory.ini"

  content = <<-EOT
[local]
localhost ansible_connection=local

[local:vars]
app_version=${var.app_version}
namespace=${var.namespace}
app_port=${var.app_port}
db_host=${var.db_host}
db_port=${var.db_port}
db_name=${var.db_name}
db_user=${var.db_user}
db_password=${var.db_password}
EOT
}
