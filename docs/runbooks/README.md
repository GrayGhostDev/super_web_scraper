```markdown
# Operational Runbooks

## Incident Response

### High Error Rate

1. Check error metrics in Grafana
2. Review error logs
3. Identify error patterns
4. Scale resources if needed
5. Roll back recent changes if applicable

```bash
# Check error rates
curl -s http://localhost:9090/api/v1/query?query=error_rate_total

# Scale deployment
kubectl scale deployment grayghost --replicas=5
```

### Service Degradation

1. Monitor system metrics
2. Check dependent services
3. Review recent changes
4. Scale resources if needed
5. Enable circuit breakers

```bash
# Check service health
curl https://api.grayghost.com/health

# Enable circuit breaker
kubectl apply -f k8s/circuit-breaker.yaml
```

## Maintenance Procedures

### Database Maintenance

1. Backup current data
2. Check disk usage
3. Run cleanup procedures
4. Verify data integrity
5. Update indexes

```bash
# Backup database
./scripts/backup.sh production

# Run maintenance
./scripts/db-maintenance.sh
```

### Cache Management

1. Monitor cache hit rates
2. Clear specific cache entries
3. Resize cache if needed
4. Verify cache consistency

```bash
# Clear cache
redis-cli FLUSHDB

# Monitor cache metrics
redis-cli INFO stats
```

## Deployment Procedures

### Rolling Update

1. Verify new version
2. Deploy to staging
3. Run smoke tests
4. Monitor metrics
5. Roll out to production

```bash
# Deploy new version
kubectl apply -k overlays/production

# Monitor rollout
kubectl rollout status deployment/grayghost
```

### Emergency Rollback

1. Identify issues
2. Stop deployment
3. Revert to previous version
4. Verify system health
5. Document incident

```bash
# Rollback deployment
kubectl rollout undo deployment/grayghost

# Verify rollback
kubectl rollout status deployment/grayghost
```
```