```python
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# Audit metrics
audit_events = Counter(
    'audit_events_total',
    'Total audit events logged',
    ['event_type', 'severity']
)

class AuditLogger:
    def __init__(self, log_file: str = 'logs/audit.log'):
        self.log_file = log_file
        self.setup_logger()

    def setup_logger(self):
        """Set up audit logger configuration."""
        audit_logger = logging.getLogger('audit')
        audit_logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
        )
        
        audit_logger.addHandler(handler)
        self.audit_logger = audit_logger

    def log_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        details: Dict[str, Any],
        severity: str = 'info',
        ip_address: Optional[str] = None
    ):
        """Log an audit event."""
        try:
            audit_events.labels(
                event_type=event_type,
                severity=severity
            ).inc()
            
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'action': action,
                'details': details,
                'severity': severity,
                'ip_address': ip_address
            }
            
            self.audit_logger.info(json.dumps(event))
            
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
            raise

    def log_security_event(
        self,
        user_id: str,
        action: str,
        success: bool,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log a security-related event."""
        severity = 'info' if success else 'warning'
        self.log_event(
            'security',
            user_id,
            action,
            details,
            severity,
            ip_address
        )

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log data access events."""
        self.log_event(
            'data_access',
            user_id,
            action,
            {
                'resource': resource,
                **details
            },
            'info',
            ip_address
        )

    def log_system_event(
        self,
        action: str,
        details: Dict[str, Any],
        severity: str = 'info'
    ):
        """Log system events."""
        self.log_event(
            'system',
            'system',
            action,
            details,
            severity
        )
```