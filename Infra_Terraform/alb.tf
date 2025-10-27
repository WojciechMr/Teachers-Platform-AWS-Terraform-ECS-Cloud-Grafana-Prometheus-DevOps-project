# =========================
# ACM Certificate (istniejący)
# =========================
resource "aws_acm_certificate" "cert" {
  domain_name       = "edublinkier.com"
  validation_method = "DNS"
}

# =========================
# Application Load Balancer
# =========================
resource "aws_lb" "app_alb" {
  name               = "app-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets

  tags = {
    Environment = var.environment
  }
}

# =========================
# Target Group (nowa TG na 8000)
# =========================
resource "aws_lb_target_group" "ecs_tg_new_8000" {
  name        = "ecs-tg-${var.environment}-8000"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Environment = var.environment
    Project     = "django-app"
  }
}

# =========================
# HTTP Listener → redirect do HTTPS
# =========================
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# =========================
# HTTPS Listener → forward do TG na 8000
# =========================
resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  
  certificate_arn = "arn:aws:acm:eu-central-1:998244281811:certificate/22cc65cb-7485-41fb-97d5-b339ceb3d78e"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg_new_8000.arn
  }
}
