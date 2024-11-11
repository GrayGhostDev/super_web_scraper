import logging
from typing import Dict, Any
import aiohttp
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class LogForwarder:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.buffer = []
        self.buffer_size = config.get('buffer_size', 100)
        self.flush_interval = config.get('flush_interval', 60)
        self.running = False
    
    async def start(self):
        """Start the log forwarder."""
        self.running = True
        while self.running:
            try:
                if len(self.buffer) >= self.buffer_size:
                    await self.flush_logs()
                await asyncio.sleep(self.flush_interval)
            except Exception as e:
                logger.error(f"Log forwarding error: {str(e)}")
                await asyncio.sleep(self.flush_interval)
    
    def stop(self):
        """Stop the log forwarder."""
        self.running = False
    
    async def add_log(self, log_entry: Dict[str, Any]):
        """Add a log entry to the buffer."""
        self.buffer.append({
            **log_entry,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def flush_logs(self):
        """Flush buffered logs to the logging service."""
        if not self.buffer:
            return
        
        try:
            logs_to_send = self.buffer[:]
            self.buffer.clear()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config['log_endpoint'],
                    json={'logs': logs_to_send},
                    headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    
        except Exception as e:
            logger.error(f"Log flush error: {str(e)}")
            # Retain logs in case of failure
            self.buffer.extend(logs_to_send)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for log forwarding request."""
        return {
            'Authorization': f"Bearer {self.config['api_key']}",
            'Content-Type': 'application/json'
        }