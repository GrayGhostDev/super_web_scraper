from typing import Dict, Any
import psutil
import logging
from datetime import datetime
import asyncio
from prometheus_client import Gauge, Counter, Histogram

logger = logging.getLogger(__name__)

# System metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_bytes', 'Memory usage in bytes')
disk_usage = Gauge('disk_usage_percent', 'Disk usage percentage')
network_io = Counter('network_io_bytes', 'Network I/O', ['direction'])
process_count = Gauge('process_count', 'Number of running processes')

# Performance metrics
system_load = Histogram(
    'system_load_avg',
    'System load average',
    ['interval']
)

class SystemMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_manager = None
        self.monitoring_interval = config.get('monitoring_interval', 60)  # seconds
        
    def setup_alert_manager(self, alert_manager):
        """Set up alert manager for notifications."""
        self.alert_manager = alert_manager
    
    async def start_monitoring(self):
        """Start system monitoring."""
        while True:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                
                # Update Prometheus metrics
                self._update_prometheus_metrics(metrics)
                
                # Check thresholds and alert if necessary
                await self._check_thresholds(metrics)
                
                # Wait for next collection interval
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            load_avg = psutil.getloadavg()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'load_avg_1min': load_avg[0],
                    'load_avg_5min': load_avg[1],
                    'load_avg_15min': load_avg[2]
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                'processes': len(psutil.pids())
            }
            
        except Exception as e:
            logger.error(f"Metrics collection error: {str(e)}")
            raise
    
    def _update_prometheus_metrics(self, metrics: Dict[str, Any]):
        """Update Prometheus metrics."""
        try:
            # Update CPU metrics
            cpu_usage.set(metrics['cpu']['usage_percent'])
            system_load.labels(interval='1min').observe(metrics['cpu']['load_avg_1min'])
            system_load.labels(interval='5min').observe(metrics['cpu']['load_avg_5min'])
            system_load.labels(interval='15min').observe(metrics['cpu']['load_avg_15min'])
            
            # Update memory metrics
            memory_usage.set(metrics['memory']['used'])
            
            # Update disk metrics
            disk_usage.set(metrics['disk']['percent'])
            
            # Update network metrics
            network_io.labels(direction='sent').inc(metrics['network']['bytes_sent'])
            network_io.labels(direction='received').inc(metrics['network']['bytes_recv'])
            
            # Update process metrics
            process_count.set(metrics['processes'])
            
        except Exception as e:
            logger.error(f"Metrics update error: {str(e)}")
    
    async def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and alert if necessary."""
        if not self.alert_manager:
            return
            
        try:
            # Check CPU usage
            if metrics['cpu']['usage_percent'] > self.config['thresholds']['cpu_percent']:
                await self.alert_manager.trigger_alert(
                    alert_type='system',
                    message=f"High CPU usage: {metrics['cpu']['usage_percent']}%",
                    severity='warning' if metrics['cpu']['usage_percent'] < 90 else 'critical'
                )
            
            # Check memory usage
            if metrics['memory']['percent'] > self.config['thresholds']['memory_percent']:
                await self.alert_manager.trigger_alert(
                    alert_type='system',
                    message=f"High memory usage: {metrics['memory']['percent']}%",
                    severity='warning' if metrics['memory']['percent'] < 90 else 'critical'
                )
            
            # Check disk usage
            if metrics['disk']['percent'] > self.config['thresholds']['disk_percent']:
                await self.alert_manager.trigger_alert(
                    alert_type='system',
                    message=f"High disk usage: {metrics['disk']['percent']}%",
                    severity='warning' if metrics['disk']['percent'] < 90 else 'critical'
                )
            
        except Exception as e:
            logger.error(f"Threshold check error: {str(e)}")
            
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            metrics = self._collect_metrics()
            return {
                'status': self._determine_system_status(metrics),
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"System status check error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _determine_system_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall system status based on metrics."""
        if (metrics['cpu']['usage_percent'] > 90 or
            metrics['memory']['percent'] > 90 or
            metrics['disk']['percent'] > 90):
            return 'critical'
        elif (metrics['cpu']['usage_percent'] > 75 or
              metrics['memory']['percent'] > 75 or
              metrics['disk']['percent'] > 75):
            return 'warning'
        return 'healthy'