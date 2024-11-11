from typing import Dict, Any
import os

class CeleryConfig:
    # Broker settings
    broker_url = f"amqp://{os.getenv('RABBITMQ_USER', 'guest')}:{os.getenv('RABBITMQ_PASS', 'guest')}@" \
                 f"{os.getenv('RABBITMQ_HOST', 'localhost')}:{os.getenv('RABBITMQ_PORT', '5672')}//"
    
    # Result backend settings
    result_backend = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
    
    # Task settings
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'UTC'
    enable_utc = True
    
    # Queue settings
    task_queues = {
        'default': {'exchange': 'default', 'routing_key': 'default'},
        'high_priority': {'exchange': 'high_priority', 'routing_key': 'high_priority'},
        'low_priority': {'exchange': 'low_priority', 'routing_key': 'low_priority'}
    }
    
    # Task routing
    task_routes = {
        'tasks.high_priority.*': {'queue': 'high_priority'},
        'tasks.low_priority.*': {'queue': 'low_priority'}
    }
    
    # Concurrency settings
    worker_prefetch_multiplier = 1
    worker_concurrency = int(os.getenv('CELERY_CONCURRENCY', '4'))
    
    # Task execution settings
    task_acks_late = True
    task_reject_on_worker_lost = True
    task_time_limit = 3600  # 1 hour
    task_soft_time_limit = 3300  # 55 minutes
    
    # Monitoring settings
    worker_send_task_events = True
    task_send_sent_event = True