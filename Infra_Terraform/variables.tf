variable "region" {
  type    = string
  default = "eu-central-1"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "domain_name" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}

variable "db_host" {
  description = "Host bazy danych PostgreSQL"
  type        = string
}

variable "django_settings_module" {
  description = "Django settings module for ECS task"
  type        = string
}


variable "email_backend" {
  type        = string
  description = "Django email backend"
}

variable "email_host" {
  type        = string
}

variable "email_port" {
  type        = number
}

variable "email_use_tls" {
  type        = bool
}

variable "email_host_user" {
  type        = string
}

variable "email_host_password" {
  type        = string
}

variable "openai_api_key" {
  type        = string
}

