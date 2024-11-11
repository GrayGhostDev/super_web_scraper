```python
import psutil
import logging
from typing import Dict, Any
from prometheus_client import Gauge, Counter, Histogram
import time

logger = logging.getLogger(__name__)

# System metrics
cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
disk_usage = Gauge('system_disk_usage_percent', 'Disk usage percentage')
disk_io = Counter('system_disk_io_bytes', 'Disk I/O', ['operation'])
network_io = Counter('system_network_io_bytes', 'Network I/O', ['direction'])

# Application metrics
api_response_time = Histogram(
    'api_response_time_seconds',
    'API response time in seconds',
    ['endpoint']
)

class SystemMetrics:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False

    async def start_collecting(self):
        """Start collecting system metrics."""
        self.running = True
        while self.running:
            try:
                self._collect_metrics()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(self.interval)

    def stop_collecting(self):
        """Stop collecting metrics."""
        self.running = False

    def _collect_metrics(self):
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

            # Disk I/O metrics
            disk_io_counters = psutil.disk_io_counters()
            disk_io.labels(operation='read').inc(disk_io_counters.read_bytes)
            disk_io.labels(operation='write').inc(disk_io_counters.write_bytes)

            # Network I/O metrics
            network = psutil.net_io_counters()
            network_io.labels(direction='sent').inc(network.bytes_sent)
            network_io.labels(direction='received').inc(network.bytes_recv)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
```