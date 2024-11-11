#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
DEPLOY_ID=$2

if [[ ! "${ENVIRONMENT}" =~ ^(staging|production)$ ]]; then
    echo "Invalid environment. Must be staging or production."
    exit 1
fi

if [ -z "${DEPLOY_ID}" ]; then
    echo "Deploy ID must be provided."
    exit 1
fi

echo "Starting rollback process..."

# Get deployment record
aws s3 cp s3://grayghost-deployments/${ENVIRONMENT}/${DEPLOY_ID}.json deployment.json

if [ ! -f deployment.json ]; then
    echo "Deployment record not found"
    exit 1
fi

# Extract deployment info
PREVIOUS_IMAGE=$(jq -r '.image' deployment.json)
PREVIOUS_SHA=$(jq -r '.sha' deployment.json)

echo "Rolling back to image: ${PREVIOUS_IMAGE}"

# Update Kubernetes deployment
kubectl set image deployment/grayghost grayghost=${PREVIOUS_IMAGE} -n grayghost

# Wait for rollout
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/grayghost -n grayghost --timeout=300s

# Verify deployment health
./deployment/scripts/health_check.sh ${ENVIRONMENT}

if [ $? -eq 0 ]; then
    echo "Rollback completed successfully!"
    
    # Update deployment record
    echo "{\"id\": \"${DEPLOY_ID}\", \"sha\": \"${PREVIOUS_SHA}\", \"image\": \"${PREVIOUS_IMAGE}\", \"rollback\": true}" > deployment.json
    aws s3 cp deployment.json s3://grayghost-deployments/${ENVIRONMENT}/latest.json
else
    echo "Rollback verification failed!"
    exit 1
fi