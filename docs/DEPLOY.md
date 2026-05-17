# Deploy

End-to-end deployment runbook for this project. Two pieces:

- **Backend** → AWS EC2 (`t4g.nano`) in `ap-south-1`, provisioned via OpenTofu.
- **Frontend** → AWS Amplify, connected to the GitHub repo via the AWS Console.

## TL;DR

```bash
# from repo root
cd infra
tofu init
tofu apply          # 14 resources; ~5 min including EC2 cloud-init
tofu output api_url # → https://13-202-206-123.sslip.io
```

Then wire Amplify (see [Frontend](#frontend-aws-amplify)) with that URL.

## Prerequisites

- AWS account with programmatic credentials configured (`aws sts get-caller-identity` works).
- `tofu` 1.7+ installed locally (`brew install opentofu`).
- The repo pushed to a public GitHub repo (so the EC2's user-data can clone it).

## Backend (AWS EC2 + Docker Compose + Caddy)

### What gets provisioned

| Resource | Purpose |
|---|---|
| `aws_instance.api` | t4g.nano (ARM Graviton, 0.5 GB RAM, ~$3/mo) running Ubuntu 24.04 |
| `aws_eip.api` | Static public IP so HTTPS cert survives instance replace |
| `aws_security_group.api` | Inbound 22, 80, 443 — outbound any |
| `aws_key_pair.ec2` | ED25519 key generated on-the-fly by OpenTofu, written to `infra/ec2_key` (gitignored) |
| `aws_s3_bucket.backups` | Nightly SQLite dumps, 30-day lifecycle |
| `aws_iam_role.ec2` + instance profile | Lets EC2 PutObject to its own bucket |

### What user-data does on first boot

1. Allocate 1 GB swap (t4g.nano's 408 MB RAM isn't enough to build Python wheels).
2. Install Docker + Compose plugin from Docker's official apt repo.
3. Install AWS CLI via `snap install aws-cli --classic` (Ubuntu 24.04 dropped the apt package).
4. Clone the configured GitHub repo into `/opt/salary-management`.
5. Compute the sslip.io hostname from the instance's public IPv4 (via IMDSv2).
6. Write `backend/.env` with `DOMAIN`, `CORS_ORIGINS`, `BACKUP_BUCKET`.
7. `docker compose build && docker compose up -d`.
8. Wait for the api container, then `alembic upgrade head`.
9. Install `/etc/cron.d/salary-backup` (nightly at 02:00 UTC).

### How HTTPS works without a domain

Caddy gets a free Let's Encrypt cert for `{eip-dashed}.sslip.io` —
`sslip.io` is a public DNS service that resolves any `1-2-3-4.sslip.io`
to IP `1.2.3.4`. Zero config. The cert is auto-renewed forever as long
as Caddy is running.

### Apply

```bash
cd infra
tofu init                # one-time provider downloads
tofu plan                # eyeball changes
tofu apply               # confirm
tofu output              # api_url, ssh_command, etc.
```

Total wall-clock: ~5 min (AWS provisioning ~75 s + cloud-init ~3–4 min for apt install + docker build on ARM).

### Seeding the deployed database

The user-data runs migrations but does not seed. Run once after apply:

```bash
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && \
     sudo docker compose exec -T api python -m salary.seed --count 10000'
```

### Debugging

```bash
# Cloud-init status (look for 'done')
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'sudo cloud-init status'

# Full bootstrap log
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'sudo tail -100 /var/log/user-data.log'

# Container status
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && sudo docker compose ps'

# Application logs
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && sudo docker compose logs --tail=100 api'
```

### Pushing a code update

```bash
# Push changes
git push

# On the EC2: pull + rebuild + restart
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management && sudo git pull && cd backend && \
     sudo docker compose up -d --build'

# If you changed the DB schema, also:
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && \
     sudo docker compose exec -T api alembic upgrade head'
```

### Tear-down

```bash
cd infra
tofu destroy
```

Wipes everything (instance, EIP, security group, key pair, S3 bucket
with its contents — `force_destroy = true`). Run when you're done
demoing to drop the bill to $0.

## Frontend (AWS Amplify)

Amplify gets a 2-minute Console setup that's better than wrestling with
its Terraform provider.

1. **AWS Amplify Console → New app → Host web app.**
2. **Source provider**: GitHub. Authorize, pick `cm1100/incubyte_work`, branch `main`.
3. **App settings**:
   - **App root directory**: `frontend`
   - **Build settings**: accept the auto-detected Next.js detection.
4. **Environment variables** (under App settings → Environment variables):
   - `NEXT_PUBLIC_API_URL` = the `api_url` from `tofu output` (e.g. `https://13-202-206-123.sslip.io`).
5. **Save and deploy.** First build ~3–4 min.

Amplify hands back a URL like `https://main.dXXXXXX.amplifyapp.com`.

### Wire CORS

After Amplify gives you that URL, SSH to EC2 and append it to
`CORS_ORIGINS`:

```bash
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip)
sudo nano /opt/salary-management/backend/.env
# Add the Amplify URL, comma-separated:
# CORS_ORIGINS=https://13-202-206-123.sslip.io,http://localhost:3000,https://main.dXXXX.amplifyapp.com
cd /opt/salary-management/backend && sudo docker compose restart api
```

## Cost

| Item | Monthly |
|---|---|
| EC2 t4g.nano | ~$3.05 |
| EBS 16 GB gp3 | ~$1.28 |
| Elastic IP (while attached) | $0 |
| S3 backups (a few MB) | <$0.01 |
| AWS Amplify (1k build min, 5 GB transfer) | $0 (free tier) |
| Data transfer out (light demo) | <$0.50 |
| **Total** | **~$5/mo** |

Run `tofu destroy` when you're done to drop to $0.
