output "cloudfront_distribution_id" {
  description = "ID da Distribuição CloudFront criada"
  value       = aws_cloudfront_distribution.ecommerce_cdn.id
}

output "cloudfront_domain_name" {
  description = "Domínio público gerado pelo CloudFront (ex: d111111abcdef8.cloudfront.net)"
  value       = aws_cloudfront_distribution.ecommerce_cdn.domain_name
}

output "frontend_s3_bucket_name" {
  description = "Nome do bucket S3 que hospeda o frontend SPA"
  value       = aws_s3_bucket.frontend.id
}

output "assets_s3_bucket_name" {
  description = "Nome do bucket S3 que armazena os assets estáticos (/images/*)"
  value       = aws_s3_bucket.assets.id
}
