import psutil
import logging
from typing import Dict, Any
from prometheus_client import Gauge, Counter, Histogram
import time

logger = logging.getLogger(__name__)

# System metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_bytes', 'Memory usage in bytes')
disk_usage = Gauge('disk_usage_percent', 'Disk usage percentage')
network_io = Counter('network_io_bytes', 'Network I/O', ['direction'])

# Application metrics
api_latency = Histogram(
    'api_latency_seconds',
    'API endpoint latency',
    ['endpoint']
)

class MetricsCollector:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False
    
    async def start_collecting(self):
        """Start collecting metrics."""
        self.running = True
        while self.running:
            try:
                self._collect_system_metrics()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(self.interval)
    
    def stop_collecting(self):
        """Stop collecting metrics."""
        self.running = False
    
    def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_usage.set(cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage.set(memory.used)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage.set(disk.percent)
            
            # Network metrics
            network = psutil.net_io_counters()
            network_io.labels(direction='sent').inc(network.bytes_sent)
            network_io.labels(direction='received').inc(network.bytes_recv)
            
        except Exception as e:
            logger.error(f"System metrics collection error: {str(e)}")
    
    @staticmethod
    def record_api_latency(endpoint: str, duration: float):
        """Record API endpoint latency."""
        api_latency.labels(endpoint=endpoint).observe(duration)