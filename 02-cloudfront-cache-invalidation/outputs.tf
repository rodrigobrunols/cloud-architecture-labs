output "cloudfront_distribution_id" {
  description = "ID da Distribuição CloudFront (usado no CI/CD para invalidação cirúrgica)"
  value       = aws_cloudfront_distribution.ecommerce_cdn.id
}

output "cloudfront_domain_name" {
  description = "Domínio público gerado pelo CloudFront"
  value       = aws_cloudfront_distribution.ecommerce_cdn.domain_name
}

output "s3_frontend_bucket_name" {
  description = "Nome do Bucket S3 para o Frontend React"
  value       = aws_s3_bucket.frontend.id
}

output "cicd_deployer_role_arn" {
  description = "ARN da Role IAM com menor privilégio para o pipeline de CI/CD"
  value       = aws_iam_role.cicd_deployer.arn
}

output "recommended_invalidation_command" {
  description = "Comando CLI recomendado para o CI/CD (Invalidação Cirúrgica)"
  value       = "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.ecommerce_cdn.id} --paths '/index.html' '/'"
}
