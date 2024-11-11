from typing import Dict
import json
import logging
from datetime import datetime
from confluent_kafka import Producer
from .kafka_config import KafkaConfig

logger = logging.getLogger(__name__)

class DataProducer:
    """Handles data production to Kafka topics"""
    
    def __init__(self, kafka_config: KafkaConfig):
        self.config = kafka_config
        self.producer = Producer({
            'bootstrap.servers': kafka_config.BOOTSTRAP_SERVERS,
            'queue.buffering.max.messages': 100000,
            'queue.buffering.max.ms': 1000,
            'batch.size': 65536,
            'linger.ms': 50
        })
    
    async def produce_raw_html(self, url: str, html_content: str):
        """Produce raw HTML content to Kafka"""
        try:
            message = {
                'url': url,
                'html_content': html_content,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.producer.produce(
                self.config.TOPICS['raw_html'],
                key=url,
                value=json.dumps(message)
            )
            self.producer.flush()
            
            await self.produce_audit_log(
                'raw_html_produced',
                {'url': url, 'status': 'success'}
            )
            
        except Exception as e:
            logger.error(f"Failed to produce raw HTML: {str(e)}")
            await self.produce_audit_log(
                'raw_html_produced',
                {'url': url, 'status': 'failed', 'error': str(e)}
            )
            raise
    
    async def produce_audit_log(self, event_type: str, event_data: Dict):
        """Produce audit log messages"""
        try:
            audit_message = {
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.producer.produce(
                self.config.TOPICS['audit_logs'],
                value=json.dumps(audit_message)
            )
            self.producer.flush()
            
        except Exception as e:
            logger.error(f"Failed to produce audit log: {str(e)}")
            raise