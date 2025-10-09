# -----------------------------
# Pobranie istniejącego SG dla ALB
# -----------------------------
data "aws_security_group" "alb_sg" {
  filter {
    name   = "group-name"
    values = ["edu-alb-sg"]
  }
}

# -----------------------------
# Application Load Balancer
# -----------------------------
resource "aws_lb" "app_lb" {
  name               = "edu-app-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [data.aws_security_group.alb_sg.id]  # teraz używamy data source
  subnets            = module.networking.public_subnets

  tags = { Name = "edu-app-alb" }
}

# -----------------------------
# Target Group dla ECS
# -----------------------------
resource "aws_lb_target_group" "platform_web_tg" {
  name        = "platform-web-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.networking.vpc_id
  target_type = "ip"

  health_check {
    path                = "/"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200,302"
  }

  tags = { Name = "platform-web-tg" }
}

# -----------------------------
# Listener HTTP 80
# -----------------------------
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.platform_web_tg.arn
  }
}

# -----------------------------
# Output DNS ALB
# -----------------------------
output "alb_dns_name" {
  value = aws_lb.app_lb.dns_name
}
