```bash
#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
ARCHIVE_TIMESTAMP=$2
ARCHIVE_BUCKET="grayghost-archives-${ENVIRONMENT}"

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

if [ -z "${ARCHIVE_TIMESTAMP}" ]; then
    echo "Archive timestamp must be provided."
    exit 1
fi

# Create restore directory
RESTORE_DIR="/tmp/grayghost_restore_${ARCHIVE_TIMESTAMP}"
mkdir -p ${RESTORE_DIR}

# Download archive from S3
echo "Downloading archive from S3..."
aws s3 cp s3://${ARCHIVE_BUCKET}/${ARCHIVE_TIMESTAMP}/archive.tar.gz ${RESTORE_DIR}/

# Extract archive
echo "Extracting archive..."
tar -xzf ${RESTORE_DIR}/archive.tar.gz -C ${RESTORE_DIR}

# Restore PostgreSQL data
echo "Restoring PostgreSQL data..."
PGPASSWORD=${POSTGRES_PASSWORD} psql \
    -h ${POSTGRES_HOST} \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    -c "\COPY profiles FROM '${RESTORE_DIR}/profiles.csv' CSV HEADER;"

# Restore Redis data
echo "Restoring Redis data..."
for file in ${RESTORE_DIR}/*.rdb; do
    key=$(basename "$file" .rdb)
    redis-cli -h ${REDIS_HOST} restore "$key" 0 "$(cat "$file")"
done

# Cleanup
echo "Cleaning up temporary files..."
rm -rf ${RESTORE_DIR}

echo "Archive restore completed successfully!"
```