# -----------------------------
# Pobranie istniejącego SG dla ECS
# -----------------------------
data "aws_security_group" "ecs_sg" {
  filter {
    name   = "group-name"
    values = ["edu-ecs-sg"]
  }
}

# ECS Service (force new deployment)
# ======================
resource "aws_ecs_service" "platform_web_service" {
  name            = "platform-web-service"
  cluster         = aws_ecs_cluster.edu_ecs_cluster.id   # Twój istniejący cluster
  desired_count   = 1
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.platform_web.arn

  network_configuration {
    subnets         = module.networking.private_subnets
    security_groups = [data.aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.platform_web_tg.arn
    container_name   = "english-platform"
    container_port   = 8000
  }

  # Minimum/Maximum dla Availability Zone Rebalancing muszą być w dopuszczalnym zakresie
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  # FORCE NEW DEPLOYMENT: wymusza restart tasków z nowym Task Definition
  lifecycle {
    ignore_changes = [task_definition]
  }

  depends_on = [
    aws_ecs_task_definition.platform_web
  ]
}