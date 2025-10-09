module "networking" {
  source      = "./modules/networking"
  vpc_cidr    = "10.0.0.0/16"
  name_prefix = "edu"
}
