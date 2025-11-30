# Pobranie najnowszego Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Security Group dla EC2 (SSM + Prometheus)
resource "aws_security_group" "ec2_ssm_sg" {
  name        = "ec2-ssm-sg"
  description = "SG for EC2 using SSM and Prometheus"
  vpc_id      = module.vpc.vpc_id



  # Ruch z EC2 do VPC endpointów (HTTPS)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block] # albo "10.0.0.0/16"
  }
  # EC2 potrzebuje tylko outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}




# IAM Role dla EC2
resource "aws_iam_role" "ec2_ssm_role" {
  name = "ec2-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}


# Attach SSM core
resource "aws_iam_role_policy_attachment" "ssm_attach" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ECS discovery policy document
data "aws_iam_policy_document" "ecs_discovery" {
  statement {
    actions = [
      "ecs:ListClusters",
      "ecs:ListServices",
      "ecs:DescribeServices",
      "ecs:ListTasks",
      "ecs:DescribeTasks",
      "ecs:DescribeTaskDefinition",
      "ecs:ListContainerInstances",
      "ecs:DescribeContainerInstances"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_discovery" {
  name        = "ecs-discovery-policy"
  description = "Allow Prometheus to perform ECS service discovery"
  policy      = data.aws_iam_policy_document.ecs_discovery.json
}

resource "aws_iam_role_policy_attachment" "ecs_discovery_attach" {
  policy_arn = aws_iam_policy.ecs_discovery.arn
  role       = aws_iam_role.ec2_ssm_role.name
}

resource "aws_iam_instance_profile" "ec2_ssm_instance_profile" {
  name = "ec2-ssm-instance-profile"
  role = aws_iam_role.ec2_ssm_role.name
}






resource "aws_instance" "ssm_ec2" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  subnet_id     = element(module.vpc.private_subnets, 0)
  security_groups = [aws_security_group.ec2_ssm_sg.id]

  iam_instance_profile = aws_iam_instance_profile.ec2_ssm_instance_profile.name

  tags = {
    Name = "prometheus-grafana"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              amazon-linux-extras install docker -y
              systemctl enable docker
              systemctl start docker
              usermod -a -G docker ec2-user
              EOF
}



output "ssm_instance_id" {
  description = "EC2 instance ID dla SSM / Prometheus"
  value       = aws_instance.ssm_ec2.id
}

output "ssm_instance_private_ip" {
  description = "Private IP EC2 w private subnet"
  value       = aws_instance.ssm_ec2.private_ip
}


