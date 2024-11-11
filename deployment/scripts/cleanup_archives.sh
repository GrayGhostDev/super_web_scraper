```bash
#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
ARCHIVE_BUCKET="grayghost-archives-${ENVIRONMENT}"
RETENTION_DAYS=365

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

# Delete old archives
echo "Cleaning up old archives..."
aws s3 ls s3://${ARCHIVE_BUCKET}/ | while read -r line; do
    timestamp=$(echo $line | awk '{print $2}' | sed 's/.$//')
    archive_date=$(date -d "${timestamp}" +%s)
    current_date=$(date +%s)
    age_days=$(( (current_date - archive_date) / 86400 ))
    
    if [ $age_days -gt $RETENTION_DAYS ]; then
        echo "Deleting archive from ${timestamp}..."
        aws s3 rm s3://${ARCHIVE_BUCKET}/${timestamp} --recursive
    fi
done

echo "Archive cleanup completed successfully!"
```