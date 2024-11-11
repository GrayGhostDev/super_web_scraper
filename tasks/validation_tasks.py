from .celery_app import app
from typing import Dict, Any
import logging
from datetime import datetime
from prometheus_client import Histogram, Counter

logger = logging.getLogger(__name__)

# Task-specific metrics
validation_duration = Histogram(
    'validation_duration_seconds',
    'Time spent validating data',
    ['validation_type']
)

validation_failures = Counter(
    'validation_failures_total',
    'Number of validation failures',
    ['validation_type']
)

@app.task(bind=True, max_retries=2)
def validate_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate profile data."""
    start_time = datetime.now()
    try:
        # Validation logic here
        result = {"status": "validated", "timestamp": datetime.utcnow().isoformat()}
        
        # Record validation duration
        duration = (datetime.now() - start_time).total_seconds()
        validation_duration.labels(validation_type='profile').observe(duration)
        
        return result
    except Exception as e:
        logger.error(f"Profile validation error: {str(e)}")
        validation_failures.labels(validation_type='profile').inc()
        self.retry(exc=e)

@app.task(bind=True, max_retries=2)
def validate_enrichment(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate enriched data."""
    start_time = datetime.now()
    try:
        # Enrichment validation logic here
        result = {"status": "validated", "timestamp": datetime.utcnow().isoformat()}
        
        # Record validation duration
        duration = (datetime.now() - start_time).total_seconds()
        validation_duration.labels(validation_type='enrichment').observe(duration)
        
        return result
    except Exception as e:
        logger.error(f"Enrichment validation error: {str(e)}")
        validation_failures.labels(validation_type='enrichment').inc()
        self.retry(exc=e)