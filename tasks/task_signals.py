from celery.signals import (
    task_prerun,
    task_postrun,
    task_success,
    task_failure,
    task_retry,
    worker_ready,
    worker_shutdown,
    celeryd_after_setup
)
import logging
from prometheus_client import Counter, Gauge
from typing import Any

logger = logging.getLogger(__name__)

# Metrics
tasks_started = Counter(
    'tasks_started_total',
    'Number of tasks started',
    ['task_name']
)

tasks_completed = Counter(
    'tasks_completed_total',
    'Number of tasks completed',
    ['task_name', 'status']
)

active_tasks = Gauge(
    'active_tasks',
    'Number of currently running tasks',
    ['task_name']
)

@task_prerun.connect
def task_prerun_handler(sender: Any = None, task_id: Any = None, **kwargs: Any) -> None:
    """Handle task pre-run events."""
    tasks_started.labels(task_name=sender.name).inc()
    active_tasks.labels(task_name=sender.name).inc()
    logger.info(f"Task {sender.name}[{task_id}] started")

@task_postrun.connect
def task_postrun_handler(sender: Any = None, task_id: Any = None, **kwargs: Any) -> None:
    """Handle task post-run events."""
    active_tasks.labels(task_name=sender.name).dec()
    logger.info(f"Task {sender.name}[{task_id}] completed")

@task_success.connect
def task_success_handler(sender: Any = None, **kwargs: Any) -> None:
    """Handle task success events."""
    tasks_completed.labels(
        task_name=sender.name,
        status='success'
    ).inc()

@task_failure.connect
def task_failure_handler(sender: Any = None, exception: Exception = None, **kwargs: Any) -> None:
    """Handle task failure events."""
    tasks_completed.labels(
        task_name=sender.name,
        status='failure'
    ).inc()
    logger.error(f"Task {sender.name} failed: {str(exception)}")

@task_retry.connect
def task_retry_handler(sender: Any = None, reason: str = None, **kwargs: Any) -> None:
    """Handle task retry events."""
    tasks_completed.labels(
        task_name=sender.name,
        status='retry'
    ).inc()
    logger.warning(f"Task {sender.name} retrying: {reason}")

@worker_ready.connect
def worker_ready_handler(**kwargs: Any) -> None:
    """Handle worker ready events."""
    logger.info("Celery worker is ready")

@worker_shutdown.connect
def worker_shutdown_handler(**kwargs: Any) -> None:
    """Handle worker shutdown events."""
    logger.info("Celery worker is shutting down")

@celeryd_after_setup.connect
def setup_direct_queue(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Set up worker queues after worker initialization."""
    logger.info(f"Worker {sender} initialized with queues: {instance.app.amqp.queues.keys()}")