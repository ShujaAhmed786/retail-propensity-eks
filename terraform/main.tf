terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket  = "retail-propensity-tfstate-639283101421"
    key     = "retail-propensity/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-1"
}

module "network" {
  source = "./modules/network"
}

module "eks" {
  source = "./modules/eks"

  private_subnet_ids = module.network.private_subnet_ids
}

module "platform" {
  source = "./modules/platform"

  cluster_name = module.eks.cluster_name
}

output "ecr_repository_url" {
  value = module.platform.ecr_repository_url
}

output "github_actions_role_arn" {
  value = module.platform.github_actions_role_arn
}

output "lb_controller_role_arn" {
  value = module.platform.lb_controller_role_arn
}
