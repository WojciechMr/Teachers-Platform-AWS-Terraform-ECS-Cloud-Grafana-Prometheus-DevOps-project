# =========================
# ECS Cluster
# =========================
resource "aws_ecs_cluster" "app_cluster" {
  name = "django-cluster-${var.environment}"
}

# =========================
# IAM Role for ECS Task Execution
# =========================
resource "aws_iam_role" "ecs_task_role" {
  name = "ecsTaskExecutionRole-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Effect    = "Allow"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# =========================
# CloudWatch Logs
# =========================
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/django-${var.environment}"
  retention_in_days = 14
}

# =========================
# ECS Task Definition
# =========================
resource "aws_ecs_task_definition" "django_task" {
  family                   = "django-task-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "django"
      image = "${aws_ecr_repository.django.repository_url}:latest"
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "DJANGO_SETTINGS_MODULE", value = var.django_settings_module },
        { name = "SECRET_KEY", value = var.django_secret_key },
        { name = "DB_ENGINE", value = "django.db.backends.postgresql" },
        { name = "DB_NAME", value = var.db_username },
        { name = "DB_USER", value = var.db_username },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_HOST", value = var.db_host },
        { name = "DB_PORT", value = "5432" },
        { name = "ALLOWED_HOSTS", value = "edublinkier.com,app-alb-prod-465977408.eu-central-1.elb.amazonaws.com" },
        { name = "OPENAI_API_KEY", value = var.openai_api_key },
        { name = "EMAIL_BACKEND", value = var.email_backend },
        { name = "EMAIL_HOST", value = var.email_host },
        { name = "EMAIL_PORT", value = tostring(var.email_port) },
        { name = "EMAIL_USE_TLS", value = tostring(var.email_use_tls) },
        { name = "EMAIL_HOST_USER", value = var.email_host_user },
        { name = "EMAIL_HOST_PASSWORD", value = var.email_host_password },
        { name = "AWS_STORAGE_BUCKET_NAME", value = var.aws_storage_bucket_name },
        { name = "AWS_S3_REGION_NAME", value = var.aws_s3_region_name }
      

      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "django"
        }
      }
    }
  ])
}

# =========================
# ECS Service
# =========================
resource "aws_ecs_service" "django_service" {
  name            = "django-service-${var.environment}"
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.django_task.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg_new_8000.arn  # <- wskazuje nową TG
    container_name   = "django"
    container_port   = 8000
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds = 60

  depends_on = [aws_lb_listener.https_listener]
}

# =========================
# AutoScaling
# =========================
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 4
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.app_cluster.name}/${aws_ecs_service.django_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu_policy" {
  name               = "cpu-scaling-${var.environment}"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    target_value       = 50.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 60
    scale_out_cooldown = 60
  }
}


# rule s3 in task Definition  

# =========================
# IAM Policy for S3 Access
# =========================
resource "aws_iam_policy" "ecs_s3_policy" {
  name   = "ecs-s3-access-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::${var.aws_storage_bucket_name}/*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:ListBucket"
        ]
        Resource = "arn:aws:s3:::${var.aws_storage_bucket_name}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_s3_policy.arn
}


