```markdown
# Troubleshooting Guide

## Common Issues

### API Connection Issues

#### Problem: API Authentication Failures
- Check API key validity
- Verify token expiration
- Ensure correct credentials in .env

Resolution:
```bash
# Verify API configuration
curl -X POST https://api.grayghost.com/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Problem: Rate Limiting
- Monitor rate limit headers
- Implement exponential backoff
- Use bulk endpoints for large operations

### Data Quality Issues

#### Problem: Low Enrichment Quality
- Check source availability
- Verify input data quality
- Review enrichment configuration

Resolution:
```python
# Check enrichment sources
await api_client.check_sources_health()
```

#### Problem: Missing Data
- Verify required fields
- Check source permissions
- Review data mapping

### Performance Issues

#### Problem: Slow Processing
1. Check system metrics
2. Monitor queue size
3. Review concurrent operations

Resolution:
```bash
# Monitor system metrics
curl http://localhost:9090/metrics | grep grayghost
```

#### Problem: Memory Usage
1. Monitor memory consumption
2. Check for memory leaks
3. Review batch sizes

### Integration Issues

#### Problem: LinkedIn Integration
- Verify OAuth configuration
- Check webhook endpoints
- Review rate limits

Resolution:
```bash
# Test LinkedIn webhook
curl -X POST https://your-domain.com/webhooks/linkedin/test
```

## Monitoring and Debugging

### Logs

Access application logs:
```bash
# View application logs
kubectl logs -f deployment/grayghost

# View specific component logs
kubectl logs -f deployment/grayghost -c api
```

### Metrics

Monitor system metrics:
1. Access Grafana dashboard
2. Check Prometheus metrics
3. Review alert history

### Health Checks

Verify system health:
```bash
# Check system health
curl https://api.grayghost.com/health

# Check component status
curl https://api.grayghost.com/health/components
```
```