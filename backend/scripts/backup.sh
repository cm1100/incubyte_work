#!/bin/bash
# Nightly SQLite dump to S3. Invoked from cron (see infra/user-data.sh).
# Runs inside the API container's environment so it sees the same DB file.

set -euo pipefail

BUCKET="${BACKUP_BUCKET:?BACKUP_BUCKET env var required}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
KEY="sqlite/app-${STAMP}.sql"
TMP=$(mktemp /tmp/app-XXXXXX.sql)

# .dump is portable across SQLite versions and produces a textual SQL file
# that's smaller than the raw DB file once gzipped.
docker compose -f /opt/salary-management/backend/docker-compose.yml exec -T api \
    sqlite3 /app/data/app.db ".dump" > "$TMP"

gzip -f "$TMP"
aws s3 cp "${TMP}.gz" "s3://${BUCKET}/${KEY}.gz"
rm -f "${TMP}.gz"

echo "Backed up to s3://${BUCKET}/${KEY}.gz"
