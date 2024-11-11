import logging
from typing import Dict, Any
import aiohttp
from datetime import datetime
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# PagerDuty metrics
pagerduty_events = Counter(
    'pagerduty_events_total',
    'Total PagerDuty events',
    ['event_type', 'severity']
)

class PagerDutyIntegration:
    def __init__(self, config: Dict[str, str]):
        self.api_key = config['pagerduty_api_key']
        self.service_id = config['pagerduty_service_id']
        self.base_url = "https://api.pagerduty.com"
        self.headers = {
            'Authorization': f'Token token={self.api_key}',
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-Type': 'application/json'
        }

    async def create_incident(
        self,
        title: str,
        description: str,
        severity: str = 'warning',
        custom_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a PagerDuty incident."""
        try:
            payload = {
                'incident': {
                    'type': 'incident',
                    'title': title,
                    'service': {
                        'id': self.service_id,
                        'type': 'service_reference'
                    },
                    'urgency': 'high' if severity == 'critical' else 'low',
                    'body': {
                        'type': 'incident_body',
                        'details': description
                    },
                    'custom_details': custom_details or {}
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/incidents",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    pagerduty_events.labels(
                        event_type='create_incident',
                        severity=severity
                    ).inc()

                    return result

        except Exception as e:
            logger.error(f"Failed to create PagerDuty incident: {str(e)}")
            raise

    async def update_incident(
        self,
        incident_id: str,
        status: str,
        resolution: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a PagerDuty incident."""
        try:
            payload = {
                'incident': {
                    'type': 'incident',
                    'status': status
                }
            }

            if resolution and status == 'resolved':
                payload['incident']['resolution'] = resolution

            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.base_url}/incidents/{incident_id}",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    pagerduty_events.labels(
                        event_type='update_incident',
                        severity='info'
                    ).inc()

                    return result

        except Exception as e:
            logger.error(f"Failed to update PagerDuty incident: {str(e)}")
            raise

    async def add_note(
        self,
        incident_id: str,
        note: str
    ) -> Dict[str, Any]:
        """Add a note to a PagerDuty incident."""
        try:
            payload = {
                'note': {
                    'content': note
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/incidents/{incident_id}/notes",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    pagerduty_events.labels(
                        event_type='add_note',
                        severity='info'
                    ).inc()

                    return result

        except Exception as e:
            logger.error(f"Failed to add note to PagerDuty incident: {str(e)}")
            raise