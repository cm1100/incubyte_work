#!/bin/bash
# Cloud-init bootstrap for the salary-management EC2.
# Runs once on first boot. Idempotent enough to re-run for debugging
# (apt-get install -y is no-op for already-installed packages, git clone
# guarded by directory check, etc.).
set -euxo pipefail

LOG=/var/log/user-data.log
exec > >(tee -a "$LOG") 2>&1
echo "[user-data] starting at $(date -u)"

# ----- swap (t4g.nano has 408 MB RAM; pip install can spike past that) -----
# 1 GB swap on the root volume is enough for the docker build phase and
# is the standard mitigation for tiny instances. EBS gp3 IOPS are plenty.
if ! swapon --show | grep -q '/swapfile'; then
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile >/dev/null
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# ----- packages -----
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
    ca-certificates curl gnupg git sqlite3

# AWS CLI: Ubuntu 24.04 dropped the apt 'awscli' package. Use snap
# (pre-installed on Ubuntu cloud images) for the official AWS-maintained
# build instead.
snap install aws-cli --classic
# Symlink so /usr/local/bin/aws is on PATH for cron-invoked scripts.
ln -sf /snap/bin/aws /usr/local/bin/aws

# Docker Engine + Compose v2 plugin from the official Docker apt repo.
# Ubuntu's distro docker.io lags well behind upstream.
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
usermod -aG docker ubuntu
systemctl enable --now docker

# ----- pull the app -----
APP_DIR=/opt/salary-management
if [ ! -d "$APP_DIR/.git" ]; then
    git clone "${clone_url}" "$APP_DIR"
fi
cd "$APP_DIR/backend"

# ----- runtime env -----
# IP is injected by Terraform templatefile — that's the EIP, not whatever
# the instance happens to boot with. Otherwise user-data races the EIP
# association and Caddy provisions a cert for the wrong sslip hostname.
PUBLIC_IP="${public_ip}"
SSLIP_HOST=$(echo "$PUBLIC_IP" | tr '.' '-').sslip.io

cat > .env <<EOF
DOMAIN=$SSLIP_HOST
# Amplify origin gets appended once the frontend is deployed.
CORS_ORIGINS=https://$SSLIP_HOST,http://localhost:3000
BACKUP_BUCKET=${backup_bucket}
EOF
echo "[user-data] DOMAIN=$SSLIP_HOST"

# ----- build & start -----
docker compose build
docker compose up -d

# ----- migrations (idempotent; alembic stamps the version table) -----
# Wait for the api container to actually be ready before running migrations.
for i in {1..30}; do
    if docker compose exec -T api python -c "import salary.db" 2>/dev/null; then
        break
    fi
    sleep 2
done
docker compose exec -T api alembic upgrade head

# ----- nightly backup cron -----
install -d -m 0755 /opt/salary-management/backend/scripts
chmod +x "$APP_DIR/backend/scripts/backup.sh"
cat > /etc/cron.d/salary-backup <<EOF
# Nightly SQLite dump to S3 at 02:00 UTC.
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
BACKUP_BUCKET=${backup_bucket}
0 2 * * * root /opt/salary-management/backend/scripts/backup.sh >> /var/log/salary-backup.log 2>&1
EOF
chmod 0644 /etc/cron.d/salary-backup

echo "[user-data] done at $(date -u). API reachable at https://$SSLIP_HOST"
