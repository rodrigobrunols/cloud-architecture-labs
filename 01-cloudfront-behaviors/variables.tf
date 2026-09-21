variable "aws_region" {
  description = "Região da AWS para provisionamento dos recursos"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto para prefixo dos recursos"
  type        = string
  default     = "ecommerce-store"
}

variable "environment" {
  description = "Ambiente de deploy (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "api_alb_dns_name" {
  description = "DNS do Application Load Balancer de Backend (ex: alb-backend-12345.us-east-1.elb.amazonaws.com)"
  type        = string
  default     = "api-backend.internal.example.com"
}
