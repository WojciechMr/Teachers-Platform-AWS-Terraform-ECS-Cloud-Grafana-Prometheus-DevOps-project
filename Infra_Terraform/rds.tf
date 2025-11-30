resource "aws_db_subnet_group" "db_subnets" {
  name       = "db-subnets-${var.environment}"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_db_instance" "db" {
  identifier              = "django-db-${var.environment}"
  engine                  = "postgres"
  engine_version          = "15.12"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids  = [aws_security_group.ecs_sg.id]
  skip_final_snapshot     = true
  publicly_accessible     = false
  multi_az                = false
  auto_minor_version_upgrade = true

 # akceptacja istniejacego stanu (dodane do rds sg group)
 
lifecycle {
    ignore_changes = [
      vpc_security_group_ids  # Terraform nie będzie nadpisywał ręcznie dodanych SG
    ]
  }
}