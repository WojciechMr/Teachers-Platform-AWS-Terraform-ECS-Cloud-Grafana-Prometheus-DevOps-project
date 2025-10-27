resource "aws_ecr_repository" "django" {
  name                 = "django-app"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Environment = "prod"
  }
}
