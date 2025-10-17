# =======================
# AWS / Region
# =======================
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "db_user" {
  description = "Alias for database username used in ECS (mapped to DB_USER)"
  type        = string
  default     = "edu_admin"
}
# =======================
# PostgreSQL / RDS
# =======================
variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "edu_db"
}

variable "db_username" {
  description = "PostgreSQL username"
  type        = string
  default     = "edu_admin"
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "db_host" {
  description = "PostgreSQL host"
  type        = string
}

variable "db_port" {
  description = "PostgreSQL port"
  type        = string
  default     = "5432"
}

# =======================
# Django
# =======================
variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
}

variable "django_debug" {
  description = "Django debug mode"
  type        = string
  default     = "True"
}

variable "django_allowed_hosts" {
  description = "Dozwolone hosty Django (oddzielone przecinkami)"
  type        = string
}

variable "image_uri" {
  description = "Adres obrazu kontenera w ECR (np. repozytorium:tag)"
  type        = string
}

variable "private_subnets" {
  type = list(string)
}


variable "image_tag" {
  description = "Tag obrazu dla ECS (np. latest)"
  type        = string
  default     = "latest"  # opcjonalnie, jeśli chcesz mieć wartość domyślną
}