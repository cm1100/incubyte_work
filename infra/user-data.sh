#!/bin/bash
# Cloud-init bootstrap for the salary-management EC2.
# Runs once on first boot. Idempotent enough to re-run for debugging
# (apt-get install -y is no-op for already-installed packages, git clone
# guarded by directory check, etc.).
set -euxo pipefail

LOG=/var/log/user-data.log
exec > >(tee -a "$LOG") 2>&1
echo "[user-data] starting at $(date -u)"

# ----- packages -----
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
    ca-certificates curl gnupg git sqlite3 awscli

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
# IP comes from instance metadata so the script works on any IP we land
# on (Elastic IP association is a separate Terraform resource and may not
# be in place at first boot).
TOKEN=$(curl -fsS -X PUT \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" \
    http://169.254.169.254/latest/api/token)
PUBLIC_IP=$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/public-ipv4)
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
