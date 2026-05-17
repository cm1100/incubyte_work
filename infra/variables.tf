variable "project" {
  type    = string
  default = "salary-management"
}

variable "region" {
  type        = string
  description = "AWS region. ap-south-1 = Mumbai."
  default     = "ap-south-1"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type. t4g.nano is ARM Graviton, ~\\$3/mo, 0.5 GB RAM."
  default     = "t4g.nano"
}

variable "github_clone_url" {
  type        = string
  description = "Public HTTPS clone URL the EC2 fetches the app from."
  default     = "https://github.com/cm1100/incubyte_work.git"
}

variable "ssh_ingress_cidr" {
  type        = string
  description = "CIDR allowed to SSH (port 22). Default 0.0.0.0/0 for assessment convenience; lock to your IP for real use."
  default     = "0.0.0.0/0"
}
