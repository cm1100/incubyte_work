output "public_ip" {
  description = "Elastic IP attached to the EC2 instance."
  value       = aws_eip.api.public_ip
}

output "sslip_hostname" {
  description = "DNS-resolvable hostname via sslip.io that Caddy uses to provision a Let's Encrypt cert."
  value       = local.sslip_hostname
}

output "api_url" {
  description = "Public HTTPS API base URL. Use this as NEXT_PUBLIC_API_URL in Amplify."
  value       = "https://${local.sslip_hostname}"
}

output "ssh_command" {
  description = "Ready-to-paste SSH command."
  value       = "ssh -i ${path.module}/ec2_key ubuntu@${aws_eip.api.public_ip}"
}

output "backups_bucket" {
  description = "S3 bucket holding nightly SQLite dumps."
  value       = aws_s3_bucket.backups.bucket
}

output "cloudfront_url" {
  description = "Public HTTPS URL served via CloudFront (global edge, TLS terminated at POP)."
  value       = "https://${aws_cloudfront_distribution.main.domain_name}"
}
