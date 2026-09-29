variable "aws_region" {
  description = "Região da AWS para provisionamento dos recursos"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto para identificação de recursos"
  type        = string
  default     = "ecommerce-cache-lab"
}

variable "environment" {
  description = "Ambiente de deployment (ex: dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "api_alb_dns_name" {
  description = "DNS do Application Load Balancer ou API Gateway do backend"
  type        = string
  default     = "api.ecommerce.internal"
}

variable "github_repo" {
  description = "Repositório GitHub (formato: organizacao/repo) para permissão via OIDC no CI/CD"
  type        = string
  default     = "rodrigobrunols/cloud-architecture-labs"
}
