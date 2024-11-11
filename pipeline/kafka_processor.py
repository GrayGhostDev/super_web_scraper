from typing import Dict
import json
import logging
from datetime import datetime
from confluent_kafka import Consumer
from .kafka_config import KafkaConfig
from .kafka_producer import DataProducer

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes data through the pipeline stages"""
    
    def __init__(self, kafka_config: KafkaConfig):
        self.config = kafka_config
        self.producer = DataProducer(kafka_config)
        
        # Initialize consumers for different stages
        self.extraction_consumer = Consumer({
            'bootstrap.servers': kafka_config.BOOTSTRAP_SERVERS,
            'group.id': kafka_config.CONSUMER_GROUPS['extraction'],
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })
        
        self.enrichment_consumer = Consumer({
            'bootstrap.servers': kafka_config.BOOTSTRAP_SERVERS,
            'group.id': kafka_config.CONSUMER_GROUPS['enrichment'],
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })
        
        self.validation_consumer = Consumer({
            'bootstrap.servers': kafka_config.BOOTSTRAP_SERVERS,
            'group.id': kafka_config.CONSUMER_GROUPS['validation'],
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })
    
    async def process_raw_html(self):
        """Process raw HTML data"""
        try:
            self.extraction_consumer.subscribe([self.config.TOPICS['raw_html']])
            
            while True:
                msg = self.extraction_consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                try:
                    # Parse message
                    data = json.loads(msg.value())
                    
                    # Extract data from HTML
                    extracted_data = await self.extract_profile_data(
                        data['html_content']
                    )
                    
                    # Produce extracted data
                    await self.producer.produce(
                        self.config.TOPICS['extracted_data'],
                        key=data['url'],
                        value=json.dumps(extracted_data)
                    )
                    
                    self.extraction_consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to process HTML: {str(e)}")
                    await self.handle_processing_failure(
                        'extraction',
                        data,
                        str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Raw HTML processing error: {str(e)}")
            raise
    
    async def enrich_profile_data(self):
        """Enrich extracted profile data"""
        try:
            self.enrichment_consumer.subscribe([self.config.TOPICS['extracted_data']])
            
            while True:
                msg = self.enrichment_consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                try:
                    # Parse message
                    data = json.loads(msg.value())
                    
                    # Enrich data with additional information
                    enriched_data = await self.enrich_data(data)
                    
                    # Produce enriched data
                    await self.producer.produce(
                        self.config.TOPICS['enriched_data'],
                        key=msg.key(),
                        value=json.dumps(enriched_data)
                    )
                    
                    self.enrichment_consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to enrich data: {str(e)}")
                    await self.handle_processing_failure(
                        'enrichment',
                        data,
                        str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Data enrichment error: {str(e)}")
            raise
    
    async def validate_profile_data(self):
        """Validate enriched profile data"""
        try:
            self.validation_consumer.subscribe([self.config.TOPICS['enriched_data']])
            
            while True:
                msg = self.validation_consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                try:
                    # Parse message
                    data = json.loads(msg.value())
                    
                    # Validate data
                    validated_data = await self.validate_data(data)
                    
                    # Produce validated data
                    await self.producer.produce(
                        self.config.TOPICS['validated_data'],
                        key=msg.key(),
                        value=json.dumps(validated_data)
                    )
                    
                    self.validation_consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to validate data: {str(e)}")
                    await self.handle_processing_failure(
                        'validation',
                        data,
                        str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Data validation error: {str(e)}")
            raise
    
    async def handle_processing_failure(
        self,
        stage: str,
        data: Dict,
        error: str
    ):
        """Handle processing failures"""
        try:
            failure_record = {
                'stage': stage,
                'data': data,
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.producer.produce(
                self.config.TOPICS['failed_processing'],
                value=json.dumps(failure_record)
            )
            
            await self.producer.produce_audit_log(
                f'{stage}_failure',
                failure_record
            )
            
        except Exception as e:
            logger.error(f"Failed to handle processing failure: {str(e)}")
            raise