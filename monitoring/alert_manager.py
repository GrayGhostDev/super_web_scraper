from typing import Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
from .pagerduty_integration import PagerDutyIntegration
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# Alert metrics
alerts_triggered = Counter(
    'alerts_triggered_total',
    'Total number of alerts triggered',
    ['severity', 'type']
)

class AlertManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pagerduty = PagerDutyIntegration(config)
        self.alert_history = []
        self.alert_handlers = {
            'critical': self._handle_critical_alert,
            'warning': self._handle_warning_alert,
            'info': self._handle_info_alert
        }

    async def handle_alert(
        self,
        alert_name: str,
        severity: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Handle incoming alerts."""
        try:
            alerts_triggered.labels(
                severity=severity,
                type=alert_name
            ).inc()

            alert_data = {
                'name': alert_name,
                'severity': severity,
                'description': description,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }

            self.alert_history.append(alert_data)

            # Route alert to appropriate handler
            if handler := self.alert_handlers.get(severity):
                await handler(alert_data)

        except Exception as e:
            logger.error(f"Error handling alert: {str(e)}")
            raise

    async def _handle_critical_alert(self, alert_data: Dict[str, Any]):
        """Handle critical alerts."""
        try:
            # Create PagerDuty incident
            await self.pagerduty.create_incident(
                title=f"CRITICAL: {alert_data['name']}",
                description=alert_data['description'],
                severity='critical',
                custom_details=alert_data['metadata']
            )

            # Send notifications
            await self._send_notifications(alert_data)

        except Exception as e:
            logger.error(f"Error handling critical alert: {str(e)}")

    async def _handle_warning_alert(self, alert_data: Dict[str, Any]):
        """Handle warning alerts."""
        try:
            # Create PagerDuty incident with lower urgency
            await self.pagerduty.create_incident(
                title=f"WARNING: {alert_data['name']}",
                description=alert_data['description'],
                severity='warning',
                custom_details=alert_data['metadata']
            )

            # Send notifications
            await self._send_notifications(alert_data)

        except Exception as e:
            logger.error(f"Error handling warning alert: {str(e)}")

    async def _handle_info_alert(self, alert_data: Dict[str, Any]):
        """Handle informational alerts."""
        try:
            # Log alert
            logger.info(f"Info alert: {alert_data['name']} - {alert_data['description']}")

            # Send notifications if configured
            if self.config.get('notify_info_alerts'):
                await self._send_notifications(alert_data)

        except Exception as e:
            logger.error(f"Error handling info alert: {str(e)}")

    async def _send_notifications(self, alert_data: Dict[str, Any]):
        """Send alert notifications through configured channels."""
        try:
            notification_tasks = []

            # Email notifications
            if self.config.get('email_notifications'):
                notification_tasks.append(
                    self._send_email_notification(alert_data)
                )

            # Slack notifications
            if self.config.get('slack_notifications'):
                notification_tasks.append(
                    self._send_slack_notification(alert_data)
                )

            await asyncio.gather(*notification_tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")

    async def _send_email_notification(self, alert_data: Dict[str, Any]):
        """Send email notification."""
        # Implement email notification logic
        pass

    async def _send_slack_notification(self, alert_data: Dict[str, Any]):
        """Send Slack notification."""
        # Implement Slack notification logic
        pass

    def get_alert_history(
        self,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get alert history with optional filtering."""
        history = self.alert_history
        
        if severity:
            history = [
                alert for alert in history
                if alert['severity'] == severity
            ]

        return sorted(
            history,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]