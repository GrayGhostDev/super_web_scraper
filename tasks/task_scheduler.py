```python
from celery.schedules import crontab
from typing import Dict, Any
from datetime import datetime
import logging
from .celery_app import app
from .profile_tasks import process_profile, update_profile
from .enrichment_tasks import enrich_profile, bulk_enrich_profiles
from .validation_tasks import validate_profile, validate_enrichment

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Manages task scheduling and periodic tasks."""
    
    def __init__(self):
        self.schedule = {
            # Profile processing tasks
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
            
            # Enrichment tasks
            'bulk-enrich-profiles': {
                'task': 'tasks.enrichment_tasks.bulk_enrich_profiles',
                'schedule': crontab(hour='*/12'),  # Every 12 hours
                'options': {'queue': 'low_priority'}
            },
            
            # Validation tasks
            'validate-profiles': {
                'task': 'tasks.validation_tasks.validate_profile',
                'schedule': crontab(hour='*/4'),  # Every 4 hours
                'options': {'queue': 'high_priority'}
            }
        }
        
        self._configure_celery()
    
    def _configure_celery(self):
        """Configure Celery beat schedule."""
        app.conf.beat_schedule = self.schedule
    
    def add_task(self, name: str, task: str, schedule: Any, options: Dict[str, Any] = None):
        """Add a new scheduled task."""
        try:
            self.schedule[name] = {
                'task': task,
                'schedule': schedule,
                'options': options or {}
            }
            self._configure_celery()
            logger.info(f"Added scheduled task: {name}")
            
        except Exception as e:
            logger.error(f"Error adding scheduled task: {str(e)}")
            raise
    
    def remove_task(self, name: str):
        """Remove a scheduled task."""
        try:
            if name in self.schedule:
                del self.schedule[name]
                self._configure_celery()
                logger.info(f"Removed scheduled task: {name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing scheduled task: {str(e)}")
            raise
    
    def update_task_schedule(self, name: str, schedule: Any):
        """Update the schedule of an existing task."""
        try:
            if name in self.schedule:
                self.schedule[name]['schedule'] = schedule
                self._configure_celery()
                logger.info(f"Updated schedule for task: {name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating task schedule: {str(e)}")
            raise
    
    def get_task_schedule(self, name: str) -> Dict[str, Any]:
        """Get the schedule configuration for a task."""
        return self.schedule.get(name)
    
    def list_scheduled_tasks(self) -> Dict[str, Any]:
        """List all scheduled tasks."""
        return {
            name: {
                'task': config['task'],
                'schedule': str(config['schedule']),
                'options': config.get('options', {})
            }
            for name, config in self.schedule.items()
        }
```