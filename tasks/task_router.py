from typing import Any, Dict
from .celery_app import app

class TaskRouter:
    """Route tasks to appropriate queues based on priority and type."""
    
    def route_for_task(self, task_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Route tasks to queues."""
        
        # High priority tasks
        if task_name.startswith('tasks.profile_tasks'):
            return {'queue': 'high_priority'}
        
        # Medium priority tasks
        if task_name.startswith('tasks.enrichment_tasks'):
            return {'queue': 'medium_priority'}
        
        # Low priority tasks
        if task_name.startswith('tasks.validation_tasks'):
            return {'queue': 'low_priority'}
        
        # Default queue for all other tasks
        return {'queue': 'default'}

app.conf.task_routes = (TaskRouter().route_for_task,)