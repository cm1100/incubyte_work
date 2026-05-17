# Deploy

Single-server deploy of both frontend and backend to one AWS EC2
(`t4g.nano`) in `ap-south-1`, provisioned via OpenTofu.

```
                                           ┌─────────────────────────────┐
                                           │  AWS EC2 t4g.nano           │
                                           │  ap-south-1                 │
                                           │  Elastic IP                 │
                  HTTPS                    │  Docker Compose:            │
  User browser ─────────────►   sslip.io ──┤    ├─ Caddy (Auto TLS,      │
                                           │    │   Let's Encrypt)       │
                                           │    │   • /api/* → api:8000  │
                                           │    │   • /*     → frontend  │
                                           │    │             :3000      │
                                           │    ├─ FastAPI (uvicorn)     │
                                           │    └─ Next.js (standalone)  │
                                           │  /var/data: SQLite          │
                                           └──────────┬──────────────────┘
                                                      │ nightly cron
                                                      ▼
                                              ┌──────────────┐
                                              │ S3 bucket    │
                                              │ (backups)    │
                                              └──────────────┘
```

## Why single-origin (not Amplify)

| | Single-EC2 | EC2 + Amplify |
|---|---|---|
| Browser interaction during deploy | **none** | one OAuth click for `gh auth login` or a PAT |
| URLs the reviewer clicks | **one** | two |
| CORS | **none — same origin** | required + has to be kept in sync |
| Build infra | Docker Compose we already shipped | new Amplify Hosting app |
| Monthly cost | ~$3 | ~$3 (Amplify free tier covers it but adds cognitive load) |
| Suitable for | small org tool, the HR-manager-of-10K-people brief | independent frontend scaling, large org |

For this assessment's persona and scope, single-origin is the right
shape. Independent frontend scaling matters at much larger scale.

## TL;DR

```bash
# from repo root
cd infra
tofu init
tofu apply          # 14 AWS resources; ~5 min through to user-data completing

# the user-data clones the repo, builds Docker images, runs alembic.
# the only thing it doesn't do is seed:
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && \
     sudo docker compose exec -T api python -m salary.seed --count 10000'

tofu output api_url
# https://13-202-206-123.sslip.io  →  UI + API both live here.
```

## Prerequisites

- AWS account with programmatic credentials (`aws sts get-caller-identity`).
- `tofu` 1.7+ (`brew install opentofu`).
- The repo pushed to a public GitHub repo (user-data clones via HTTPS).

## What gets provisioned

| Resource | Purpose |
|---|---|
| `aws_instance.api` | t4g.nano (ARM Graviton, 0.5 GB RAM, ~$3/mo) running Ubuntu 24.04 |
| `aws_eip.api` | Static public IP so HTTPS cert survives instance replace |
| `aws_security_group.api` | Inbound 22, 80, 443; outbound any |
| `aws_key_pair.ec2` | ED25519 key generated on-the-fly by OpenTofu → `infra/ec2_key` (gitignored) |
| `aws_s3_bucket.backups` | Nightly SQLite dumps, 30-day lifecycle |
| `aws_iam_role.ec2` + instance profile | EC2 → S3 write permission |

## What user-data does on first boot

1. Allocate 1 GB swap (t4g.nano's 408 MB RAM isn't enough for the npm/pip build phases).
2. Install Docker + Compose plugin from Docker's official apt repo.
3. Install AWS CLI via `snap install aws-cli --classic` (Ubuntu 24.04 dropped the apt package).
4. Clone the repo into `/opt/salary-management`.
5. Write `backend/.env` with `DOMAIN={eip}.sslip.io`, `CORS_ORIGINS`, `BACKUP_BUCKET` (EIP comes from Terraform templatefile, not IMDS — avoids the EIP-association race).
6. `docker compose build && docker compose up -d` for **api + frontend + caddy**.
7. Wait for the api container, then `alembic upgrade head`.
8. Install `/etc/cron.d/salary-backup` (nightly at 02:00 UTC).

## How HTTPS works without a domain

Caddy gets a free Let's Encrypt cert for `{eip-dashed}.sslip.io` —
`sslip.io` is a public DNS service that resolves `1-2-3-4.sslip.io`
to IP `1.2.3.4`. Zero config, auto-renewed forever.

## Seeding the deployed database

```bash
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && \
     sudo docker compose exec -T api python -m salary.seed --count 10000 --reset'
```

## Debugging

```bash
# Cloud-init status ('done' = bootstrap finished)
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) 'sudo cloud-init status'

# Full bootstrap log
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) 'sudo tail -100 /var/log/user-data.log'

# Container status
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && sudo docker compose ps'

# Application logs (any service)
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && sudo docker compose logs --tail=100 api'
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && sudo docker compose logs --tail=100 frontend'
```

## Pushing a code update

```bash
git push

ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management && sudo git stash && sudo git pull && \
     cd backend && sudo docker compose up -d --build'

# DB schema change? also run:
ssh -i ec2_key ubuntu@$(tofu output -raw public_ip) \
    'cd /opt/salary-management/backend && \
     sudo docker compose exec -T api alembic upgrade head'
```

`git stash` first because user-data marks `scripts/backup.sh` executable
(modifies the file), which trips `git pull --rebase` otherwise.

## Tear-down

```bash
cd infra
tofu destroy
```

Wipes everything (instance, EIP, security group, key pair, S3 bucket
with its contents — `force_destroy = true`). Run when done demoing.

## Cost

| Item | Monthly |
|---|---|
| EC2 t4g.nano | ~$3.05 |
| EBS 16 GB gp3 | ~$1.28 |
| Elastic IP (while attached) | $0 |
| S3 backups (a few MB) | <$0.01 |
| Data transfer (light demo) | <$0.50 |
| **Total** | **~$5/mo** |

Tear down between demos to drop to $0.

## Bugs caught and fixed during this deploy

Honest list — see git log for the actual commits:

1. **`awscli` not in Ubuntu 24.04 apt** → switched to `snap install aws-cli`.
2. **Dockerfile copied source after `pip install`** — `pip install .` failed because `src/` wasn't visible when setuptools tried to discover packages.
3. **`def list` shadowed `list[dict]` annotation** on Python 3.12. Local Python 3.14 has PEP 649 lazy annotations enabled so the import never failed locally. Fixed with `from __future__ import annotations`.
4. **EIP-vs-IMDS race**: user-data captured the EC2's *temporary* public IP before the Elastic IP attached. Caddy got a Let's Encrypt cert for the wrong sslip hostname. Fixed by passing the EIP into the user-data via Terraform's `templatefile`.
5. **`seed_data/` outside the package** → not shipped by `pip install`. Moved inside `src/salary/seed_data/` and added `package-data` config in pyproject.toml.

Each was caught by smoke-testing against the deployed instance, not just by tests passing locally.
