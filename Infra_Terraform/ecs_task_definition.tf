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
      image     = "998244281811.dkr.ecr.eu-central-1.amazonaws.com/english-platform:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "DB_NAME", value = "edu_db" },
        { name = "DB_USER", value = "edu_admin" },
        { name = "DB_PASSWORD", value = "maniekirlandia1" },
        { name = "DB_HOST", value = "edu-db-public.cbuk8souypno.eu-central-1.rds.amazonaws.com" },
        { name = "DB_PORT", value = "5432" },
        { name = "DJANGO_SECRET_KEY", value = "q6v$ysg&2sx%&gdn@qz&nlnt83r5wwyql(+wne#&b=fl2=*t3a" },
        { name = "DJANGO_DEBUG", value = "True" }
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
