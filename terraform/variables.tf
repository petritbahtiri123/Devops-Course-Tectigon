variable "app_version" {
  type    = string
  default = "v1"
}

variable "namespace" {
  type    = string
  default = "final-task"
}

variable "app_port" {
  type    = number
  default = 5000
}

variable "db_host" {
  type    = string
  default = "postgres"
}

variable "db_port" {
  type    = number
  default = 5432
}

variable "db_name" {
  type    = string
  default = "appdb"
}

variable "db_user" {
  type    = string
  default = "appuser"
}

variable "db_password" {
  type    = string
  default = "apppass"
}
