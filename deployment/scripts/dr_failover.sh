```bash
#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
if [[ ! "${ENVIRONMENT}" =~ ^(staging|production)$ ]]; then
    echo "Invalid environment. Must be staging or production."
    exit 1
fi

# Load DR configuration
source /etc/dr-config/recovery-regions

echo "Starting disaster recovery failover..."

# Update DNS
echo "Updating DNS to secondary region..."
aws route53 change-resource-record-sets \
    --hosted-zone-id ${HOSTED_ZONE_ID} \
    --change-batch '{
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "api.grayghost.com",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "'${secondary_lb_zone}'",
                    "DNSName": "'${secondary_lb_dns}'",
                    "EvaluateTargetHealth": true
                }
            }
        }]
    }'

# Restore database
echo "Restoring database in secondary region..."
aws s3 cp \
    s3://grayghost-dr-backup-${secondary}/database/latest/ \
    /tmp/db_backup \
    --recursive \
    --region ${secondary}

PGPASSWORD=${POSTGRES_PASSWORD} psql \
    -h ${POSTGRES_HOST_SECONDARY} \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    -f /tmp/db_backup/base.sql

# Restore Redis
echo "Restoring Redis in secondary region..."
aws s3 cp \
    s3://grayghost-dr-backup-${secondary}/redis/latest/redis.rdb \
    /tmp/redis.rdb \
    --region ${secondary}

redis-cli -h ${REDIS_HOST_SECONDARY} -a ${REDIS_PASSWORD} FLUSHALL
redis-cli -h ${REDIS_HOST_SECONDARY} -a ${REDIS_PASSWORD} CONFIG SET dir /tmp
redis-cli -h ${REDIS_HOST_SECONDARY} -a ${REDIS_PASSWORD} CONFIG SET dbfilename redis.rdb
redis-cli -h ${REDIS_HOST_SECONDARY} -a ${REDIS_PASSWORD} SAVE

# Scale up applications in secondary region
echo "Scaling up applications in secondary region..."
kubectl config use-context ${SECONDARY_CLUSTER}
kubectl scale deployment grayghost --replicas=5 -n grayghost

# Verify health
echo "Verifying application health..."
for i in {1..30}; do
    if curl -s https://api.grayghost.com/health | grep -q "healthy"; then
        echo "Application is healthy in secondary region"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Health check failed after 5 minutes"
        exit 1
    fi
    sleep 10
done

# Clean up
rm -rf /tmp/db_backup /tmp/redis.rdb

echo "Failover completed successfully!"
```