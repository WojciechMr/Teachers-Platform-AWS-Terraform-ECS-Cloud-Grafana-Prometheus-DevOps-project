resource "aws_ecs_cluster" "edu_ecs_cluster" {
  name = "edu-ecs-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  lifecycle {
    prevent_destroy = true
  }
}
