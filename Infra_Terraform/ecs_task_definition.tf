# Pobranie istniejącej roli ECS Task Execution
data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

# Utworzenie log group w CloudWatch
resource "aws_cloudwatch_log_group" "ecs_platform_web" {
  name              = "/ecs/english-platform"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "platform_web" {
  family                   = "platform-web"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "english-platform"
      image     = var.image_uri
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
          
        }
      ]
      environment = [
        { name = "DB_NAME", value = var.db_name },
        { name = "DB_USER", value = var.db_user },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_HOST", value = var.db_host },
        { name = "DB_PORT", value = var.db_port },
        { name = "DJANGO_SECRET_KEY", value = var.django_secret_key },
        { name = "DJANGO_DEBUG", value = var.django_debug },
        # <- Tutaj wszystkie hosty w jednej linii po przecinku
        { name = "DJANGO_ALLOWED_HOSTS", value = var.django_allowed_hosts },
        { name = "DJANGO_SETTINGS_MODULE", value = "web.settings" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_platform_web.name
          awslogs-region        = "eu-central-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
