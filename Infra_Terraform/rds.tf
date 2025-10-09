# -----------------------------
# RDS Subnet Group – prywatne subnety
# -----------------------------
resource "aws_db_subnet_group" "rds_subnets" {
  name       = "${var.db_username}-subnet-group"
  subnet_ids = [
    "subnet-006e53fefc47afafe", # edu-private-0
    "subnet-0b2f681707884d09b"  # edu-private-1
  ]
  tags = {
    Name = "${var.db_username}-rds-subnet-group"
  }
}

# -----------------------------
# RDS Instance – istniejąca instancja
# -----------------------------
resource "aws_db_instance" "postgres" {
  # Podstawowe ustawienia – muszą pasować do istniejącej instancji
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "17.4"  # dopasowane do aktualnej wersji RDS
  instance_class         = "db.t3.micro"
  db_name                = "edu_db"
  username               = var.db_username
  password               = var.db_password  # lub pozostaw puste, jeśli nie chcesz zmieniać
  db_subnet_group_name   = aws_db_subnet_group.rds_subnets.name
  vpc_security_group_ids = ["sg-0b8a30deed4dbac61"]
  skip_final_snapshot    = true
  publicly_accessible    = false

  lifecycle {
    ignore_changes = [
      engine_version,
      password,
      allocated_storage,
      vpc_security_group_ids,
      publicly_accessible,
      storage_encrypted,
      multi_az
    ]
  }

  tags = {
    Name = "edu_postgres_db"
  }
}

# -----------------------------
# Security Group Rule: ECS może łączyć się do RDS
# -----------------------------
resource "aws_security_group_rule" "ecs_to_rds" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = "sg-0b8a30deed4dbac61" # edu-rds-sg
  source_security_group_id = "sg-02e18eadcb60c8f00" # edu-ecs-sg
}

# -----------------------------
# OUTPUTS
# -----------------------------
output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_port" {
  description = "Port of the RDS instance"
  value       = aws_db_instance.postgres.port
}

output "rds_username" {
  description = "Username for the RDS instance"
  value       = aws_db_instance.postgres.username
}

output "rds_db_name" {
  description = "Database name of the RDS instance"
  value       = aws_db_instance.postgres.db_name
}

output "rds_subnet_group" {
  description = "RDS subnet group name"
  value       = aws_db_subnet_group.rds_subnets.name
}

output "rds_security_group_id" {
  description = "Security group ID of the RDS"
  value       = "sg-0b8a30deed4dbac61"
}
