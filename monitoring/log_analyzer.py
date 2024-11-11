import logging
from typing import Dict, Any, List
import re
from datetime import datetime, timedelta
from collections import defaultdict
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Log analysis metrics
log_entries_processed = Counter(
    'log_entries_processed_total',
    'Total number of log entries processed',
    ['log_type']
)

error_patterns_detected = Counter(
    'error_patterns_detected_total',
    'Total number of error patterns detected',
    ['pattern_type']
)

analysis_duration = Histogram(
    'log_analysis_duration_seconds',
    'Time spent analyzing logs',
    ['analysis_type']
)

class LogAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_patterns = self._compile_error_patterns()
        self.alert_manager = None  # Initialize in setup
    
    def setup_alert_manager(self, alert_manager):
        """Set up alert manager for notifications."""
        self.alert_manager = alert_manager
    
    async def analyze_logs(
        self,
        log_entries: List[Dict[str, Any]],
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Analyze log entries for patterns and anomalies."""
        start_time = datetime.now()
        
        try:
            # Process log entries
            analysis_results = {
                'error_patterns': self._analyze_error_patterns(log_entries),
                'frequency_analysis': self._analyze_frequency(log_entries, time_window),
                'severity_distribution': self._analyze_severity(log_entries),
                'component_health': self._analyze_component_health(log_entries)
            }
            
            # Record metrics
            duration = (datetime.now() - start_time).total_seconds()
            analysis_duration.labels(analysis_type='full').observe(duration)
            
            # Trigger alerts if necessary
            await self._check_alert_conditions(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Log analysis error: {str(e)}")
            raise
    
    def _compile_error_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for error detection."""
        return {
            'api_error': re.compile(r'API (error|failure|timeout)'),
            'database_error': re.compile(r'(database|DB) (error|failure|timeout)'),
            'authentication_error': re.compile(r'(auth|authentication) (error|failure)'),
            'validation_error': re.compile(r'validation (error|failure)'),
            'rate_limit': re.compile(r'rate limit exceeded'),
            'memory_error': re.compile(r'(memory|OOM|out of memory)'),
            'connection_error': re.compile(r'(connection|connectivity) (error|failure)')
        }
    
    def _analyze_error_patterns(self, log_entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze logs for known error patterns."""
        pattern_counts = defaultdict(int)
        
        for entry in log_entries:
            message = entry.get('message', '')
            for pattern_name, pattern in self.error_patterns.items():
                if pattern.search(message):
                    pattern_counts[pattern_name] += 1
                    error_patterns_detected.labels(pattern_type=pattern_name).inc()
        
        return dict(pattern_counts)
    
    def _analyze_frequency(
        self,
        log_entries: List[Dict[str, Any]],
        time_window: timedelta
    ) -> Dict[str, Any]:
        """Analyze log entry frequency."""
        now = datetime.now()
        window_start = now - time_window
        
        frequency_data = defaultdict(int)
        for entry in log_entries:
            timestamp = entry.get('timestamp')
            if timestamp and timestamp >= window_start:
                hour = timestamp.strftime('%H:00')
                frequency_data[hour] += 1
        
        return dict(frequency_data)
    
    def _analyze_severity(self, log_entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of log severity levels."""
        severity_counts = defaultdict(int)
        
        for entry in log_entries:
            severity = entry.get('severity', 'unknown').lower()
            severity_counts[severity] += 1
        
        return dict(severity_counts)
    
    def _analyze_component_health(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze component health based on log patterns."""
        component_health = defaultdict(lambda: {'errors': 0, 'warnings': 0})
        
        for entry in log_entries:
            component = entry.get('component', 'unknown')
            severity = entry.get('severity', '').lower()
            
            if severity == 'error':
                component_health[component]['errors'] += 1
            elif severity == 'warning':
                component_health[component]['warnings'] += 1
        
        return {
            component: {
                'status': 'healthy' if data['errors'] == 0 else 'degraded' if data['errors'] < 5 else 'unhealthy',
                'metrics': data
            }
            for component, data in component_health.items()
        }
    
    async def _check_alert_conditions(self, analysis_results: Dict[str, Any]):
        """Check if analysis results warrant alerts."""
        if not self.alert_manager:
            logger.warning("Alert manager not configured")
            return
        
        # Check error pattern thresholds
        for pattern, count in analysis_results['error_patterns'].items():
            threshold = self.config['alert_thresholds'].get(pattern, 5)
            if count >= threshold:
                await self.alert_manager.trigger_alert(
                    alert_type='error_pattern',
                    message=f"Error pattern '{pattern}' exceeded threshold: {count} occurrences",
                    severity='warning' if count < threshold * 2 else 'critical',
                    metadata={'pattern': pattern, 'count': count}
                )
        
        # Check component health
        for component, health in analysis_results['component_health'].items():
            if health['status'] == 'unhealthy':
                await self.alert_manager.trigger_alert(
                    alert_type='component_health',
                    message=f"Component '{component}' is unhealthy",
                    severity='critical',
                    metadata={
                        'component': component,
                        'errors': health['metrics']['errors'],
                        'warnings': health['metrics']['warnings']
                    }
                )