from .celery_app import app
from typing import Dict, Any
import logging
from datetime import datetime
from prometheus_client import Histogram

logger = logging.getLogger(__name__)

# Task-specific metrics
profile_processing_duration = Histogram(
    'profile_processing_duration_seconds',
    'Time spent processing profiles',
    ['operation']
)

@app.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    rate_limit='100/m'
)
def process_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single profile."""
    start_time = datetime.now()
    try:
        # Process profile logic here
        result = {"status": "processed", "timestamp": datetime.utcnow().isoformat()}
        
        # Record processing duration
        duration = (datetime.now() - start_time).total_seconds()
        profile_processing_duration.labels(operation='process').observe(duration)
        
        return result
    except Exception as e:
        logger.error(f"Profile processing error: {str(e)}")
        self.retry(exc=e)

@app.task(bind=True, max_retries=3)
def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing profile."""
    start_time = datetime.now()
    try:
        # Update profile logic here
        result = {"status": "updated", "timestamp": datetime.utcnow().isoformat()}
        
        # Record processing duration
        duration = (datetime.now() - start_time).total_seconds()
        profile_processing_duration.labels(operation='update').observe(duration)
        
        return result
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        self.retry(exc=e)