# ----- CloudFront in front of the EC2 -----------------------------------

# AWS-managed cache + origin-request policies — beats hand-crafting them.
#
# CachingDisabled: TTL=0, no query-string-based cache key. Right for the
# default behaviour because /api/* is dynamic and /employees is SSR.
#
# CachingOptimized: long TTL with the standard cache key (URL + Accept-
# Encoding). Used only for /_next/static/* below, which Next.js content-
# hashes — safe to cache forever.
#
# AllViewerExceptHostHeader: forward all viewer headers (cookies, etc.)
# EXCEPT Host. We need this because we want CloudFront to send the
# *origin's* hostname (sslip.io) as Host so Caddy's {$DOMAIN} matcher
# fires, not the viewer's cloudfront.net hostname.
data "aws_cloudfront_cache_policy" "disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_cache_policy" "optimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_except_host" {
  name = "Managed-AllViewerExceptHostHeader"
}

resource "aws_cloudfront_distribution" "main" {
  comment             = "${var.project} front door"
  enabled             = true
  is_ipv6_enabled     = true
  http_version        = "http2and3"
  price_class         = "PriceClass_100" # US + EU + India edges; cheapest
  default_root_object = ""               # Next.js owns routing
  retain_on_delete    = false
  wait_for_deployment = true

  origin {
    origin_id   = "ec2-sslip"
    domain_name = local.sslip_hostname # 13-202-206-123.sslip.io

    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_protocol_policy   = "https-only"
      origin_ssl_protocols     = ["TLSv1.2"]
      origin_keepalive_timeout = 60
      origin_read_timeout      = 30
    }
  }

  default_cache_behavior {
    target_origin_id       = "ec2-sslip"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]

    cache_policy_id          = data.aws_cloudfront_cache_policy.disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id
  }

  # Next.js content-hashes every file under /_next/static/*, so a 1y TTL
  # is safe — the hash changes when the bundle changes.
  ordered_cache_behavior {
    path_pattern           = "/_next/static/*"
    target_origin_id       = "ec2-sslip"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    cache_policy_id = data.aws_cloudfront_cache_policy.optimized.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
  }
}
