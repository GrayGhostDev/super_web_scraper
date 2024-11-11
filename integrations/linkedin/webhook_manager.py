```python
import logging
from typing import Dict, Any, Callable, List
import hmac
import hashlib
import json
from datetime import datetime
from prometheus_client import Counter, Histogram
import asyncio
from aiohttp import web

logger = logging.getLogger(__name__)

# Webhook metrics
webhook_events = Counter(
    'linkedin_webhook_events_total',
    'LinkedIn webhook events',
    ['event_type', 'status']
)

webhook_processing = Histogram(
    'linkedin_webhook_processing_seconds',
    'Webhook processing duration',
    ['event_type']
)

class LinkedInWebhookManager:
    def __init__(self, config: Dict[str, str]):
        self.signing_secret = config['webhook_signing_secret']
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.retry_config = {
            'max_retries': 3,
            'initial_delay': 1,
            'max_delay': 10
        }

    async def handle_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming webhook requests."""
        try:
            # Verify signature
            if not await self._verify_signature(request):
                webhook_events.labels(
                    event_type='unknown',
                    status='invalid_signature'
                ).inc()
                logger.error("Invalid webhook signature")
                return web.Response(status=401)

            # Parse payload
            payload = await request.json()
            
            # Process events
            await self._process_events(payload)
            
            return web.Response(status=200)
            
        except Exception as e:
            webhook_events.labels(
                event_type='unknown',
                status='error'
            ).inc()
            logger.error(f"Webhook handling error: {str(e)}")
            return web.Response(status=500)

    async def _verify_signature(self, request: web.Request) -> bool:
        """Verify webhook signature."""
        try:
            signature = request.headers.get('X-LinkedIn-Signature')
            if not signature:
                return False

            body = await request.read()
            computed_signature = hmac.new(
                self.signing_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, computed_signature)
            
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False

    async def _process_events(self, payload: Dict[str, Any]) -> None:
        """Process webhook events."""
        events = payload.get('events', [])
        
        for event in events:
            event_type = event.get('eventType')
            if not event_type:
                continue

            with webhook_processing.labels(event_type=event_type).time():
                webhook_events.labels(
                    event_type=event_type,
                    status='received'
                ).inc()
                
                handlers = self.event_handlers.get(event_type, [])
                for handler in handlers:
                    try:
                        await self._execute_with_retry(handler, event)
                        webhook_events.labels(
                            event_type=event_type,
                            status='processed'
                        ).inc()
                    except Exception as e:
                        webhook_events.labels(
                            event_type=event_type,
                            status='error'
                        ).inc()
                        logger.error(
                            f"Event handler error for {event_type}: {str(e)}"
                        )

    async def _execute_with_retry(
        self,
        handler: Callable,
        event: Dict[str, Any]
    ) -> None:
        """Execute handler with retry logic."""
        retries = 0
        delay = self.retry_config['initial_delay']

        while retries < self.retry_config['max_retries']:
            try:
                await handler(event)
                return
            except Exception as e:
                retries += 1
                if retries == self.retry_config['max_retries']:
                    logger.error(
                        f"Handler failed after {retries} retries: {str(e)}"
                    )
                    raise

                logger.warning(
                    f"Handler failed (attempt {retries}), retrying: {str(e)}"
                )
                await asyncio.sleep(delay)
                delay = min(
                    delay * 2,
                    self.retry_config['max_delay']
                )

    def register_handler(
        self,
        event_type: str,
        handler: Callable
    ) -> None:
        """Register event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def unregister_handler(
        self,
        event_type: str,
        handler: Callable
    ) -> bool:
        """Unregister event handler."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
```