from celery.schedules import crontab
from typing import Dict, Any
from .celery_app import app
from .profile_tasks import process_profile, update_profile
from .enrichment_tasks import enrich_profile, bulk_enrich_profiles
from .validation_tasks import validate_profile, validate_enrichment

# Schedule configuration
CELERYBEAT_SCHEDULE: Dict[str, Any] = {
    'process-profiles': {
        'task': 'tasks.profile_tasks.process_profile',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {'queue': 'high_priority'}
    },
    'update-profiles': {
        'task': 'tasks.profile_tasks.update_profile',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'options': {'queue': 'low_priority'}
    },
    'bulk-enrich-profiles': {
        'task': 'tasks.enrichment_tasks.bulk_enrich_profiles',
        'schedule': crontab(hour='*/12'),  # Every 12 hours
        'options': {'queue': 'low_priority'}
    },
    'validate-profiles': {
        'task': 'tasks.validation_tasks.validate_profile',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
        'options': {'queue': 'high_priority'}
    }
}

app.conf.beat_schedule = CELERYBEAT_SCHEDULE