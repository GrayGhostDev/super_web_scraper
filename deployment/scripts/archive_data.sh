```bash
#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
ARCHIVE_BUCKET="grayghost-archives-${ENVIRONMENT}"
RETENTION_DAYS=90
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

# Create archive directory
ARCHIVE_DIR="/tmp/grayghost_archive_${TIMESTAMP}"
mkdir -p ${ARCHIVE_DIR}

# Archive old data from PostgreSQL
echo "Archiving old PostgreSQL data..."
PGPASSWORD=${POSTGRES_PASSWORD} psql \
    -h ${POSTGRES_HOST} \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    -c "\COPY (SELECT * FROM profiles WHERE updated_at < NOW() - INTERVAL '${RETENTION_DAYS} days') TO '${ARCHIVE_DIR}/profiles.csv' CSV HEADER;"

# Archive old Redis data
echo "Archiving old Redis data..."
redis-cli -h ${REDIS_HOST} --scan "profile:*" | while read key; do
    ttl=$(redis-cli -h ${REDIS_HOST} ttl "$key")
    if [ $ttl -lt $((RETENTION_DAYS * 86400)) ]; then
        redis-cli -h ${REDIS_HOST} dump "$key" > "${ARCHIVE_DIR}/${key}.rdb"
        redis-cli -h ${REDIS_HOST} del "$key"
    fi
done

# Create archive
echo "Creating archive..."
tar -czf ${ARCHIVE_DIR}.tar.gz -C ${ARCHIVE_DIR} .

# Upload to S3
echo "Uploading archive to S3..."
aws s3 cp ${ARCHIVE_DIR}.tar.gz s3://${ARCHIVE_BUCKET}/${TIMESTAMP}/

# Cleanup
echo "Cleaning up temporary files..."
rm -rf ${ARCHIVE_DIR} ${ARCHIVE_DIR}.tar.gz

echo "Archive completed successfully!"
```