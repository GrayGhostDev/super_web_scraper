from celery import Celery
from celery.signals import task_success, task_failure
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery('gray_ghost_tasks')

# Configure Celery
app.conf.update(
    broker_url=f"amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASS')}@"
              f"{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}//",
    result_backend=f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0",
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'tasks.profile_tasks.*': {'queue': 'profile_queue'},
        'tasks.enrichment_tasks.*': {'queue': 'enrichment_queue'},
        'tasks.validation_tasks.*': {'queue': 'validation_queue'}
    },
    task_default_queue='default',
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True
)

# Prometheus metrics
task_success_counter = Counter(
    'task_success_total',
    'Number of successful task executions',
    ['task_name']
)

task_failure_counter = Counter(
    'task_failure_total',
    'Number of failed task executions',
    ['task_name']
)

task_duration_histogram = Histogram(
    'task_duration_seconds',
    'Task execution duration in seconds',
    ['task_name']
)

active_tasks_gauge = Gauge(
    'active_tasks',
    'Number of currently running tasks',
    ['task_name']
)

@task_success.connect
def task_success_handler(sender=None, **kwargs):
    """Handle successful task completion."""
    task_name = sender.name
    task_success_counter.labels(task_name=task_name).inc()
    active_tasks_gauge.labels(task_name=task_name).dec()

@task_failure.connect
def task_failure_handler(sender=None, **kwargs):
    """Handle task failure."""
    task_name = sender.name
    task_failure_counter.labels(task_name=task_name).inc()
    active_tasks_gauge.labels(task_name=task_name).dec()