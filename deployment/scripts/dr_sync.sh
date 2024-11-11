```bash
#!/bin/bash
set -e

# Load configuration
source /etc/dr-config/recovery-regions

# Sync database to secondary region
echo "Syncing database to secondary region..."
pg_basebackup \
    -h ${POSTGRES_HOST} \
    -U ${POSTGRES_USER} \
    -D /tmp/db_backup \
    -Fp \
    -Xs \
    -P

# Upload backup to S3 in secondary region
echo "Uploading database backup to secondary region..."
aws s3 cp \
    /tmp/db_backup \
    s3://grayghost-dr-backup-${secondary}/database/ \
    --recursive \
    --region ${secondary}

# Sync Redis data
echo "Syncing Redis data..."
redis-cli -h ${REDIS_HOST} --rdb /tmp/redis.rdb
aws s3 cp \
    /tmp/redis.rdb \
    s3://grayghost-dr-backup-${secondary}/redis/ \
    --region ${secondary}

# Sync application state
echo "Syncing application state..."
aws s3 sync \
    s3://grayghost-state-${primary} \
    s3://grayghost-state-${secondary} \
    --region ${secondary}

# Clean up temporary files
rm -rf /tmp/db_backup /tmp/redis.rdb

echo "DR sync completed successfully!"
```