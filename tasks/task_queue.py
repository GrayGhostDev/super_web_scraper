```python
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from prometheus_client import Counter, Gauge
from .celery_app import app
from .task_monitor import TaskMonitor

logger = logging.getLogger(__name__)

# Queue metrics
queue_size = Gauge(
    'task_queue_size',
    'Number of tasks in queue',
    ['queue_name']
)

queue_operations = Counter(
    'queue_operations_total',
    'Total queue operations',
    ['operation', 'queue_name']
)

class TaskQueue:
    """Manages task queues and task routing."""
    
    def __init__(self):
        self.monitor = TaskMonitor()
        self.queues = {
            'high_priority': {
                'max_size': 1000,
                'workers': 4
            },
            'medium_priority': {
                'max_size': 5000,
                'workers': 2
            },
            'low_priority': {
                'max_size': 10000,
                'workers': 1
            }
        }
    
    async def submit_task(
        self,
        task_name: str,
        *args: Any,
        queue: str = 'medium_priority',
        **kwargs: Any
    ) -> Optional[str]:
        """Submit a task to the queue."""
        try:
            # Validate queue
            if queue not in self.queues:
                raise ValueError(f"Invalid queue: {queue}")
            
            # Check queue size
            if not await self._check_queue_size(queue):
                logger.error(f"Queue {queue} is full")
                return None
            
            # Submit task
            task = app.send_task(
                task_name,
                args=args,
                kwargs=kwargs,
                queue=queue
            )
            
            # Update metrics
            queue_operations.labels(
                operation='submit',
                queue_name=queue
            ).inc()
            queue_size.labels(queue_name=queue).inc()
            
            # Start monitoring
            self.monitor.record_task_start(task_name, task.id)
            
            return task.id
            
        except Exception as e:
            logger.error(f"Error submitting task: {str(e)}")
            return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        try:
            app.control.revoke(task_id, terminate=True)
            self.monitor.record_task_completion(task_id, 'cancelled')
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling task: {str(e)}")
            return False
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and information."""
        try:
            task = app.AsyncResult(task_id)
            return {
                'id': task_id,
                'status': task.status,
                'result': task.result if task.ready() else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting task status: {str(e)}")
            return {
                'id': task_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_queue_size(self, queue_name: str) -> bool:
        """Check if queue has capacity."""
        try:
            queue_config = self.queues[queue_name]
            current_size = await self._get_queue_size(queue_name)
            return current_size < queue_config['max_size']
            
        except Exception as e:
            logger.error(f"Error checking queue size: {str(e)}")
            return False
    
    async def _get_queue_size(self, queue_name: str) -> int:
        """Get current queue size."""
        try:
            i = app.control.inspect()
            active = i.active()
            reserved = i.reserved()
            
            if not active or not reserved:
                return 0
            
            total_tasks = 0
            for worker in active:
                total_tasks += sum(1 for task in active[worker]
                                 if task['delivery_info']['routing_key'] == queue_name)
            for worker in reserved:
                total_tasks += sum(1 for task in reserved[worker]
                                 if task['delivery_info']['routing_key'] == queue_name)
            
            return total_tasks
            
        except Exception as e:
            logger.error(f"Error getting queue size: {str(e)}")
            return 0
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        stats = {}
        for queue_name, config in self.queues.items():
            stats[queue_name] = {
                'max_size': config['max_size'],
                'workers': config['workers'],
                'current_size': queue_size.labels(queue_name=queue_name)._value.get()
            }
        return stats
```