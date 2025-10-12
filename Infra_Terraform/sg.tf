# SG dla ALB
resource "aws_security_group" "alb_sg" {
  name        = "edu-alb-sg"
  description = "Security Group for ALB"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

    ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "edu-alb-sg" }
}

# SG dla ECS Tasks
resource "aws_security_group" "ecs_sg" {
  name        = "edu-ecs-sg"
  description = "Security Group for ECS tasks"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]  # ruch tylko z ALB
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "edu-ecs-sg" }

  lifecycle {
    ignore_changes = [
      ingress,
      egress,
      description
    ]
  }
}

# SG dla RDS
resource "aws_security_group" "rds_sg" {
  name        = "edu-rds-sg"
  description = "Security Group for RDS"
  vpc_id      = module.networking.vpc_id

  # Ruch z ECS
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]  # tylko ECS może się połączyć
  }

  # Ruch z Twojego lokalnego IP
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["84.195.196.201/32"]  # Twój lokalny adres IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "edu-rds-sg" }

  lifecycle {
    ignore_changes = [
      ingress,
      egress,
      description
    ]
  }
}
