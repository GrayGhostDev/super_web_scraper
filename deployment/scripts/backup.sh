#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
BACKUP_BUCKET="grayghost-backups-${ENVIRONMENT}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

# Create backup directory
BACKUP_DIR="/tmp/grayghost_backup_${TIMESTAMP}"
mkdir -p ${BACKUP_DIR}

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
PGPASSWORD=${POSTGRES_PASSWORD} pg_dump \
    -h ${POSTGRES_HOST} \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    -F c \
    -f ${BACKUP_DIR}/database.dump

# Backup Redis data
echo "Backing up Redis data..."
redis-cli -h ${REDIS_HOST} --rdb ${BACKUP_DIR}/redis.rdb

# Create archive
echo "Creating backup archive..."
tar -czf ${BACKUP_DIR}.tar.gz -C ${BACKUP_DIR} .

# Upload to S3
echo "Uploading backup to S3..."
aws s3 cp ${BACKUP_DIR}.tar.gz s3://${BACKUP_BUCKET}/${TIMESTAMP}/

# Cleanup
echo "Cleaning up temporary files..."
rm -rf ${BACKUP_DIR} ${BACKUP_DIR}.tar.gz

echo "Backup completed successfully!"