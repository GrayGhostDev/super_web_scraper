#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
HEALTH_CHECK_URL="https://api.grayghost.com/health"

# Validate environment
if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
    echo "Invalid environment. Must be development, staging, or production."
    exit 1
fi

# Perform health check
echo "Performing health check..."
response=$(curl -s -w "\n%{http_code}" ${HEALTH_CHECK_URL})
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo "Health check passed!"
    exit 0
else
    echo "Health check failed with status code: ${http_code}"
    echo "Response body: ${body}"
    exit 1
fi