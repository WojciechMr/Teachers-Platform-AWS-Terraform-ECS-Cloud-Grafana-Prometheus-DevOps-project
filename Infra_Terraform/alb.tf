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
# resource "aws_lb_listener" "http" {
#  load_balancer_arn = aws_lb.app_lb.arn
#  port              = 80
#  protocol          = "HTTP"
#
#  default_action {
#    type             = "forward"
#    target_group_arn = aws_lb_target_group.platform_web_tg.arn
#  }
#}

# -----------------------------
# Output DNS ALB
# -----------------------------
output "alb_dns_name" {
  value = aws_lb.app_lb.dns_name
}


#############################
# ZMIENNE
#############################
variable "domain_name" {
  description = "Nazwa domeny głównej (np. edublinkier.com)"
  type        = string
  default     = "edublinkier.com"
}

#############################
# ROUTE 53 — ZONE
#############################
data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

#############################
# CERTYFIKAT ACM (DNS VALIDATION)
#############################
resource "aws_acm_certificate" "cert" {
  domain_name               = var.domain_name
  subject_alternative_names = ["www.${var.domain_name}"]
  validation_method         = "DNS"

  tags = {
    Name = "edublinkier-acm-cert"
  }
}

# Rekordy DNS do walidacji certyfikatu
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => dvo
  }

  zone_id = data.aws_route53_zone.main.zone_id
  name    = each.value.resource_record_name
  type    = each.value.resource_record_type
  ttl     = 60
  records = [each.value.resource_record_value]
}

# Walidacja certyfikatu ACM
resource "aws_acm_certificate_validation" "cert_validation_complete" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

#############################
# LISTENER HTTPS (443)
#############################
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.platform_web_tg.arn
  }

  depends_on = [aws_acm_certificate_validation.cert_validation_complete]
}

#############################
# REDIRECT z HTTP -> HTTPS
#############################
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.app_lb.arn
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

#############################
# ROUTE 53 — ALIAS RECORDS
#############################

# Główna domena (edublinkier.com)
resource "aws_route53_record" "alb_alias_root" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.app_lb.dns_name
    zone_id                = aws_lb.app_lb.zone_id
    evaluate_target_health = true
  }

  depends_on = [aws_acm_certificate_validation.cert_validation_complete]
}

# Subdomena www (www.edublinkier.com)
resource "aws_route53_record" "alb_alias_www" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.app_lb.dns_name
    zone_id                = aws_lb.app_lb.zone_id
    evaluate_target_health = true
  }

  depends_on = [aws_acm_certificate_validation.cert_validation_complete]
}

#############################
# OUTPUTS
#############################
output "https_domain_url" {
  description = "Publiczny adres HTTPS aplikacji"
  value       = "https://${var.domain_name}"
}

output "https_www_domain_url" {
  description = "Publiczny adres HTTPS aplikacji z www"
  value       = "https://www.${var.domain_name}"
}
