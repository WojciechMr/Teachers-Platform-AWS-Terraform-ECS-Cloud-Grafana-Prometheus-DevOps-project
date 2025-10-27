terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket = "edukac-platform-terraform-backend"
    key    = "prod/terraform.tfstate"
    region = "eu-central-1"
  }
}

provider "aws" {
  region = "eu-central-1"
}
