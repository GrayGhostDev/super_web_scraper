#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
BACKUP_TIMESTAMP=$2
BACKUP_BUCKET="grayghost-backups-${ENVIRONMENT}"

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

if [ -z "${BACKUP_TIMESTAMP}" ]; then
    echo "Backup timestamp must be provided."
    exit 1
fi

# Create restore directory
RESTORE_DIR="/tmp/grayghost_restore_${BACKUP_TIMESTAMP}"
mkdir -p ${RESTORE_DIR}

# Download backup from S3
echo "Downloading backup from S3..."
aws s3 cp s3://${BACKUP_BUCKET}/${BACKUP_TIMESTAMP}/backup.tar.gz ${RESTORE_DIR}/

# Extract archive
echo "Extracting backup archive..."
tar -xzf ${RESTORE_DIR}/backup.tar.gz -C ${RESTORE_DIR}

# Restore PostgreSQL database
echo "Restoring PostgreSQL database..."
PGPASSWORD=${POSTGRES_PASSWORD} pg_restore \
    -h ${POSTGRES_HOST} \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    -c \
    ${RESTORE_DIR}/database.dump

# Restore Redis data
echo "Restoring Redis data..."
redis-cli -h ${REDIS_HOST} FLUSHALL
redis-cli -h ${REDIS_HOST} -n 0 < ${RESTORE_DIR}/redis.rdb

# Cleanup
echo "Cleaning up temporary files..."
rm -rf ${RESTORE_DIR}

echo "Restore completed successfully!"