#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
AWS_REGION="us-west-2"
ECR_REPOSITORY="grayghost"
CLUSTER_NAME="grayghost-${ENVIRONMENT}"

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t ${ECR_REPOSITORY}:latest .

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag and push image
echo "Pushing image to ECR..."
docker tag ${ECR_REPOSITORY}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Update kubeconfig
echo "Updating kubeconfig..."
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}

# Apply Kubernetes configurations
echo "Applying Kubernetes configurations..."
kubectl apply -k kubernetes/overlays/${ENVIRONMENT}

# Wait for rollout
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/grayghost -n grayghost

echo "Deployment completed successfully!"