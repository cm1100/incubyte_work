locals {
  # Caddy gets a Let's Encrypt cert for {dashed-ip}.sslip.io, which is a
  # public DNS service that resolves any 1-2-3-4.sslip.io to IP 1.2.3.4.
  # Saves us a domain registration + Route 53 hosted zone fees.
  sslip_hostname = "${replace(aws_eip.api.public_ip, ".", "-")}.sslip.io"
}

# ----- AMI ---------------------------------------------------------------

# Ubuntu 24.04 LTS, ARM64, picked from Canonical's official AMIs in this region.
data "aws_ami" "ubuntu_arm64" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-arm64-server-*"]
  }
  filter {
    name   = "architecture"
    values = ["arm64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ----- SSH key on the fly ------------------------------------------------

# Generating in OpenTofu instead of asking the operator to manage a key
# means `tofu apply` is self-contained. Private key is marked sensitive
# and written to a gitignored local file.
resource "tls_private_key" "ec2" {
  algorithm = "ED25519"
}

resource "aws_key_pair" "ec2" {
  key_name   = "${var.project}-ec2"
  public_key = tls_private_key.ec2.public_key_openssh
}

resource "local_sensitive_file" "ec2_key" {
  filename        = "${path.module}/ec2_key"
  content         = tls_private_key.ec2.private_key_openssh
  file_permission = "0600"
}

# ----- Security group ---------------------------------------------------

resource "aws_security_group" "api" {
  name        = "${var.project}-api"
  description = "Public HTTPS API + SSH access for the salary-management backend"

  ingress {
    description = "SSH (lock to your IP for non-assessment use)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ingress_cidr]
  }

  ingress {
    description = "HTTP (Caddy ACME challenge + redirect to 443)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS API"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ----- EC2 instance + Elastic IP ----------------------------------------

resource "aws_instance" "api" {
  ami                         = data.aws_ami.ubuntu_arm64.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.ec2.key_name
  vpc_security_group_ids      = [aws_security_group.api.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  associate_public_ip_address = true

  root_block_device {
    volume_size = 16
    volume_type = "gp3"
    encrypted   = true
  }

  # The bootstrap script clones the repo, installs Docker, and brings the
  # stack up. Re-reading the file at apply time means an edit to the
  # template forces a re-provision.
  user_data = templatefile("${path.module}/user-data.sh", {
    clone_url     = var.github_clone_url
    backup_bucket = aws_s3_bucket.backups.bucket
  })

  # Replace the instance if user-data changes — otherwise edits to the
  # bootstrap script silently do nothing on existing instances.
  user_data_replace_on_change = true

  tags = {
    Name = "${var.project}-api"
  }
}

resource "aws_eip" "api" {
  domain = "vpc"
  tags   = { Name = "${var.project}-api" }
}

resource "aws_eip_association" "api" {
  instance_id   = aws_instance.api.id
  allocation_id = aws_eip.api.id
}
