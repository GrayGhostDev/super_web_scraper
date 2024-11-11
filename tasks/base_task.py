from celery import Task
import logging
from typing import Any, Dict
from prometheus_client import Counter, Histogram
import time

logger = logging.getLogger(__name__)

# Task metrics
task_duration = Histogram(
    'task_duration_seconds',
    'Task execution duration in seconds',
    ['task_name']
)

task_errors = Counter(
    'task_errors_total',
    'Number of task errors',
    ['task_name', 'error_type']
)

class BaseTask(Task):
    """Base task class with common functionality."""
    
    abstract = True
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute task with metrics and logging."""
        start_time = time.time()
        
        try:
            result = super().__call__(*args, **kwargs)
            
            # Record task duration
            duration = time.time() - start_time
            task_duration.labels(task_name=self.name).observe(duration)
            
            return result
            
        except Exception as e:
            # Record error metrics
            task_errors.labels(
                task_name=self.name,
                error_type=type(e).__name__
            ).inc()
            
            logger.error(f"Task error in {self.name}: {str(e)}")
            raise
    
    def on_failure(self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        """Handle task failure."""
        logger.error(
            f"Task {self.name}[{task_id}] failed: {str(exc)}\n"
            f"Args: {args}\nKwargs: {kwargs}"
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        """Handle task retry."""
        logger.warning(
            f"Task {self.name}[{task_id}] retrying: {str(exc)}\n"
            f"Args: {args}\nKwargs: {kwargs}"
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval: Any, task_id: str, args: Any, kwargs: Any) -> None:
        """Handle task success."""
        logger.info(f"Task {self.name}[{task_id}] completed successfully")
        super().on_success(retval, task_id, args, kwargs)
    
    def apply_async(self, args: Any = None, kwargs: Any = None, **options: Any) -> Any:
        """Override to add default task options."""
        options.setdefault('retry', True)
        options.setdefault('retry_policy', {
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.5,
        })
        return super().apply_async(args, kwargs, **options)