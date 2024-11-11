```python
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from prometheus_client import Counter, Gauge, Histogram
import asyncio

logger = logging.getLogger(__name__)

# Task monitoring metrics
task_executions = Counter(
    'task_executions_total',
    'Total number of task executions',
    ['task_name', 'status']
)

task_duration = Histogram(
    'task_duration_seconds',
    'Task execution duration',
    ['task_name']
)

active_tasks = Gauge(
    'active_tasks',
    'Number of currently running tasks',
    ['task_name']
)

class TaskMonitor:
    """Monitors task execution and performance."""
    
    def __init__(self):
        self.task_history = {}
        self.active_tasks = {}
    
    async def start_monitoring(self):
        """Start task monitoring."""
        while True:
            try:
                await self._update_metrics()
                await self._check_task_health()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Task monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    def record_task_start(self, task_name: str, task_id: str):
        """Record task start event."""
        try:
            current_time = datetime.utcnow()
            self.active_tasks[task_id] = {
                'name': task_name,
                'start_time': current_time
            }
            active_tasks.labels(task_name=task_name).inc()
            
        except Exception as e:
            logger.error(f"Error recording task start: {str(e)}")
    
    def record_task_completion(
        self,
        task_id: str,
        status: str,
        result: Any = None
    ):
        """Record task completion event."""
        try:
            if task_id in self.active_tasks:
                task_info = self.active_tasks[task_id]
                task_name = task_info['name']
                duration = (datetime.utcnow() - task_info['start_time']).total_seconds()
                
                # Update metrics
                task_executions.labels(
                    task_name=task_name,
                    status=status
                ).inc()
                task_duration.labels(task_name=task_name).observe(duration)
                active_tasks.labels(task_name=task_name).dec()
                
                # Update history
                self.task_history[task_id] = {
                    'name': task_name,
                    'start_time': task_info['start_time'],
                    'end_time': datetime.utcnow(),
                    'duration': duration,
                    'status': status,
                    'result': result
                }
                
                del self.active_tasks[task_id]
                
        except Exception as e:
            logger.error(f"Error recording task completion: {str(e)}")
    
    async def _update_metrics(self):
        """Update task monitoring metrics."""
        try:
            # Clean up old history
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.task_history = {
                task_id: info
                for task_id, info in self.task_history.items()
                if info['end_time'] > cutoff_time
            }
            
            # Update active tasks
            for task_id, info in list(self.active_tasks.items()):
                duration = (datetime.utcnow() - info['start_time']).total_seconds()
                if duration > 3600:  # 1 hour timeout
                    self.record_task_completion(task_id, 'timeout')
                    
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
    
    async def _check_task_health(self):
        """Check task health and performance."""
        try:
            task_stats = {}
            
            # Calculate task statistics
            for task_info in self.task_history.values():
                task_name = task_info['name']
                if task_name not in task_stats:
                    task_stats[task_name] = {
                        'total': 0,
                        'success': 0,
                        'failure': 0,
                        'durations': []
                    }
                
                stats = task_stats[task_name]
                stats['total'] += 1
                stats['durations'].append(task_info['duration'])
                if task_info['status'] == 'success':
                    stats['success'] += 1
                else:
                    stats['failure'] += 1
            
            # Log health issues
            for task_name, stats in task_stats.items():
                if stats['total'] > 0:
                    failure_rate = stats['failure'] / stats['total']
                    avg_duration = sum(stats['durations']) / len(stats['durations'])
                    
                    if failure_rate > 0.1:  # More than 10% failure rate
                        logger.warning(
                            f"High failure rate for task {task_name}: "
                            f"{failure_rate:.2%}"
                        )
                    
                    if avg_duration > 300:  # Average duration > 5 minutes
                        logger.warning(
                            f"High average duration for task {task_name}: "
                            f"{avg_duration:.2f} seconds"
                        )
                        
        except Exception as e:
            logger.error(f"Error checking task health: {str(e)}")
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task execution statistics."""
        stats = {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.task_history),
            'task_types': {}
        }
        
        for task_info in self.task_history.values():
            task_name = task_info['name']
            if task_name not in stats['task_types']:
                stats['task_types'][task_name] = {
                    'total': 0,
                    'success': 0,
                    'failure': 0,
                    'avg_duration': 0
                }
            
            task_stats = stats['task_types'][task_name]
            task_stats['total'] += 1
            if task_info['status'] == 'success':
                task_stats['success'] += 1
            else:
                task_stats['failure'] += 1
            task_stats['avg_duration'] = (
                (task_stats['avg_duration'] * (task_stats['total'] - 1) +
                 task_info['duration']) / task_stats['total']
            )
        
        return stats
```