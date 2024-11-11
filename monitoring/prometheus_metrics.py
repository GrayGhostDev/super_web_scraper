from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    start_http_server
)
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# API Metrics
api_requests = Counter(
    'api_requests_total',
    'Total API requests made',
    ['api_name', 'endpoint', 'method']
)

api_errors = Counter(
    'api_errors_total',
    'Total API errors encountered',
    ['api_name', 'error_type']
)

api_response_time = Histogram(
    'api_response_time_seconds',
    'API response times in seconds',
    ['api_name', 'endpoint']
)

# Pipeline Metrics
pipeline_processing_time = Histogram(
    'pipeline_processing_time_seconds',
    'Pipeline processing time in seconds',
    ['stage']
)

pipeline_errors = Counter(
    'pipeline_errors_total',
    'Total pipeline errors encountered',
    ['stage', 'error_type']
)

active_pipelines = Gauge(
    'active_pipelines',
    'Number of active pipeline processes',
    ['stage']
)

# Data Quality Metrics
data_quality_score = Summary(
    'data_quality_score',
    'Data quality scores',
    ['data_type']
)

validation_failures = Counter(
    'validation_failures_total',
    'Total validation failures',
    ['validation_type']
)

# Resource Usage Metrics
memory_usage = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['component']
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage',
    ['component']
)

def start_metrics_server(port: int = 9090):
    """Start the Prometheus metrics server."""
    try:
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {str(e)}")
        raise

def record_api_metrics(api_name: str, endpoint: str, method: str, duration: float, error: Exception = None):
    """Record API-related metrics."""
    api_requests.labels(api_name=api_name, endpoint=endpoint, method=method).inc()
    api_response_time.labels(api_name=api_name, endpoint=endpoint).observe(duration)
    
    if error:
        api_errors.labels(api_name=api_name, error_type=type(error).__name__).inc()

def record_pipeline_metrics(stage: str, duration: float, error: Exception = None):
    """Record pipeline-related metrics."""
    pipeline_processing_time.labels(stage=stage).observe(duration)
    
    if error:
        pipeline_errors.labels(stage=stage, error_type=type(error).__name__).inc()

def update_resource_metrics(component: str, memory: float, cpu: float):
    """Update resource usage metrics."""
    memory_usage.labels(component=component).set(memory)
    cpu_usage.labels(component=component).set(cpu)