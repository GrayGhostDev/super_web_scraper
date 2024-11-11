```markdown
# Deployment Procedures

## Environment Setup

### Prerequisites

1. AWS Account Configuration
```bash
# Configure AWS CLI
aws configure

# Verify configuration
aws sts get-caller-identity
```

2. Kubernetes Tools
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

3. Database Setup
```bash
# Create database
kubectl apply -f k8s/database/

# Run migrations
alembic upgrade head
```

## Deployment Process

### 1. Infrastructure Deployment

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan
```

### 2. Application Deployment

```bash
# Deploy application
kubectl apply -k overlays/production

# Verify deployment
kubectl get pods
kubectl get services
```

### 3. Post-Deployment Verification

```bash
# Check system health
curl https://api.grayghost.com/health

# Monitor logs
kubectl logs -f deployment/grayghost

# Check metrics
curl http://localhost:9090/metrics
```

## Scaling Procedures

### Horizontal Scaling

```bash
# Scale application
kubectl scale deployment grayghost --replicas=5

# Verify scaling
kubectl get pods
```

### Vertical Scaling

```bash
# Update resource requests
kubectl set resources deployment grayghost \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi
```

## Backup Procedures

### Database Backup

```bash
# Create backup
./scripts/backup.sh production

# Verify backup
aws s3 ls s3://grayghost-backups/
```

### Application State

```bash
# Export configuration
kubectl get configmap -o yaml > config-backup.yaml

# Export secrets
kubectl get secrets -o yaml > secrets-backup.yaml
```

## Monitoring Setup

### Prometheus & Grafana

```bash
# Deploy monitoring stack
helm install monitoring prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/monitoring-grafana 3000:80
```

### Alerts Configuration

```bash
# Configure alert manager
kubectl apply -f monitoring/alertmanager-config.yaml

# Verify alerts
curl http://localhost:9093/api/v1/alerts
```

## Security Procedures

### Certificate Management

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.8.0/cert-manager.yaml

# Create certificate
kubectl apply -f k8s/certificates/
```

### Secret Management

```bash
# Create secrets
kubectl create secret generic api-keys \
  --from-file=./secrets/api-keys.yaml

# Verify secrets
kubectl get secrets
```

## Rollback Procedures

### Application Rollback

```bash
# View rollout history
kubectl rollout history deployment/grayghost

# Rollback to previous version
kubectl rollout undo deployment/grayghost

# Verify rollback
kubectl rollout status deployment/grayghost
```

### Database Rollback

```bash
# Restore database
./scripts/restore.sh production <backup-id>

# Verify restoration
alembic current
```
```