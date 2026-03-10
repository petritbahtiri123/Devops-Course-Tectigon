output "app_version" {
  value = var.app_version
}

output "namespace" {
  value = var.namespace
}

output "k8s_values_file" {
  value = local_file.k8s_values.filename
}

output "inventory_file" {
  value = local_file.inventory.filename
}
