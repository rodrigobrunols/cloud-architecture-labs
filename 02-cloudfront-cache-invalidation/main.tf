terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ==============================================================================
# AWS MANAGED POLICIES DATA SOURCES
# ==============================================================================

data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_except_host" {
  name = "Managed-AllViewerExceptHostHeader"
}

# Política Customizada de Cache para a API de Catálogo (com suporte a Query Strings & SWR)
resource "aws_cloudfront_cache_policy" "catalog_api_cache_policy" {
  name        = "${var.project_name}-catalog-cache-policy"
  comment     = "Cache para API de Catalogo e Produtos (TTL 60s + Query Strings no Cache Key)"
  default_ttl = 60
  max_ttl     = 300
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none" # APIs de catálogo não variam por cookie
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "all" # Importante: ?page=1, ?cat=shoes são cacheados separadamente
    }
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# ==============================================================================
# ORIGIN ACCESS CONTROL (OAC) FOR SECURE S3 ORIGINS
# ==============================================================================

resource "aws_cloudfront_origin_access_control" "s3_oac" {
  name                              = "${var.project_name}-s3-oac"
  description                       = "OAC para acesso seguro do CloudFront ao S3"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ==============================================================================
# S3 BUCKET PARA FRONTEND SPA E ASSETS
# ==============================================================================

resource "aws_s3_bucket" "frontend" {
  bucket        = "${var.project_name}-${var.environment}-frontend"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Política do Bucket S3 autorizando exclusivamente o CloudFront via OAC
data "aws_iam_policy_document" "s3_oac_frontend_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.frontend.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.ecommerce_cdn.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.s3_oac_frontend_policy.json
}

# ==============================================================================
# CLOUDFRONT DISTRIBUTION COM MÚLTIPLOS BEHAVIORS E INVALIDAÇÃO CIRÚRGICA
# ==============================================================================

resource "aws_cloudfront_distribution" "ecommerce_cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  comment             = "E-Commerce App - Multiple API Behaviors & Cache Invalidation (${var.environment})"

  # ----------------------------------------------------------------------------
  # ORIGENS
  # ----------------------------------------------------------------------------

  # Origem 1: S3 Frontend SPA & Hashed Assets
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3-Frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_oac.id
  }

  # Origem 2: ALB Backend APIs
  origin {
    domain_name = var.api_alb_dns_name
    origin_id   = "ALB-Backend"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # ----------------------------------------------------------------------------
  # BEHAVIOR 0: /assets/* e /static/* (JS/CSS versionados com HASH)
  # Estratégia: Cache de 1 ano (31536000s) + compressão Brotli/Gzip.
  # NUNCA requer invalidação no CloudFront após deploys.
  # ----------------------------------------------------------------------------
  ordered_cache_behavior {
    path_pattern     = "/assets/*"
    target_origin_id = "S3-Frontend"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD"]

    cache_policy_id        = data.aws_cloudfront_cache_policy.caching_optimized.id
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # ----------------------------------------------------------------------------
  # BEHAVIOR 1: /api/catalog/* e /api/products/* (API de Catálogo / Vitrine)
  # Estratégia: Edge Cache ativo (TTL 60s + SWR) com cache por Query String
  # ----------------------------------------------------------------------------
  ordered_cache_behavior {
    path_pattern     = "/api/catalog/*"
    target_origin_id = "ALB-Backend"

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD"]

    cache_policy_id          = aws_cloudfront_cache_policy.catalog_api_cache_policy.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # ----------------------------------------------------------------------------
  # BEHAVIOR 2: /api/* (APIs Transacionais: Checkout, Carrinho, Auth)
  # Estratégia: Cache desativado, repassa headers, cookies e query parameters.
  # ----------------------------------------------------------------------------
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    target_origin_id = "ALB-Backend"

    allowed_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods  = ["GET", "HEAD"]

    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id

    viewer_protocol_policy = "redirect-to-https"
  }

  # ----------------------------------------------------------------------------
  # DEFAULT BEHAVIOR: SPA Entrypoint (index.html e rotas do React)
  # Estratégia: Cache com revalidação obrigatória.
  # Único objeto que sofre invalidação no CI/CD: /index.html
  # ----------------------------------------------------------------------------
  default_cache_behavior {
    target_origin_id       = "S3-Frontend"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.caching_optimized.id
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
  }

  # Fallback para Client-Side Routing (React Router)
  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# ==============================================================================
# IAM ROLE & POLICIES COM MENOR PRIVILÉGIO PARA O PIPELINE DE CI/CD
# ==============================================================================

data "aws_iam_policy_document" "cicd_deployer_policy" {
  statement {
    sid       = "AllowS3Deploy"
    actions   = ["s3:PutObject", "s3:GetObject", "s3:ListBucket", "s3:DeleteObject"]
    resources = [
      aws_s3_bucket.frontend.arn,
      "${aws_s3_bucket.frontend.arn}/*"
    ]
  }

  statement {
    sid       = "AllowCloudFrontSurgicalInvalidation"
    actions   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
    resources = [aws_cloudfront_distribution.ecommerce_cdn.arn]
  }
}

resource "aws_iam_policy" "cicd_deployer" {
  name        = "${var.project_name}-cicd-deployer-policy"
  description = "Política de menor privilégio para deploy e invalidação no CI/CD"
  policy      = data.aws_iam_policy_document.cicd_deployer_policy.json
}

data "aws_iam_policy_document" "cicd_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "cicd_deployer" {
  name               = "${var.project_name}-cicd-deployer-role"
  assume_role_policy = data.aws_iam_policy_document.cicd_trust_policy.json
}

resource "aws_iam_role_policy_attachment" "cicd_attach" {
  role       = aws_iam_role.cicd_deployer.name
  policy_arn = aws_iam_policy.cicd_deployer.arn
}
