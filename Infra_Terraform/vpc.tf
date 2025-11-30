module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.5.0"

  name = "django-vpc-${var.environment}"
  cidr = var.vpc_cidr

  azs             = ["eu-central-1a", "eu-central-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Environment = var.environment
  }
}




# SSM
resource "aws_vpc_endpoint" "ssm" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.eu-central-1.ssm"
  vpc_endpoint_type = "Interface"
  security_group_ids = [aws_security_group.ec2_ssm_sg.id]
  subnet_ids        = module.vpc.private_subnets
  private_dns_enabled = true
}

# EC2Messages
resource "aws_vpc_endpoint" "ec2messages" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.eu-central-1.ec2messages"
  vpc_endpoint_type = "Interface"
  security_group_ids = [aws_security_group.ec2_ssm_sg.id]
  subnet_ids        = module.vpc.private_subnets
  private_dns_enabled = true
}

# SSM Messages
resource "aws_vpc_endpoint" "ssmmessages" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.eu-central-1.ssmmessages"
  vpc_endpoint_type = "Interface"
  security_group_ids = [aws_security_group.ec2_ssm_sg.id]
  subnet_ids        = module.vpc.private_subnets
  private_dns_enabled = true
}