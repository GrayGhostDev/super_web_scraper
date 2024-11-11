from typing import Dict
import logging
from confluent_kafka.admin import NewTopic, AdminClient
from .kafka_config import KafkaConfig

logger = logging.getLogger(__name__)

class KafkaPipelineManager:
    """Manages Kafka topics and pipeline setup"""
    
    def __init__(self, kafka_config: KafkaConfig):
        self.config = kafka_config
        self.admin_client = AdminClient({'bootstrap.servers': kafka_config.BOOTSTRAP_SERVERS})
    
    async def setup_pipeline(self):
        """Initialize Kafka topics and configure pipeline"""
        try:
            # Define topic configurations
            topic_configs = {
                'raw_html': {
                    'retention.ms': 86400000,  # 24 hours
                    'cleanup.policy': 'delete'
                },
                'extracted_data': {
                    'retention.ms': 172800000,  # 48 hours
                    'cleanup.policy': 'compact'
                },
                'enriched_data': {
                    'retention.ms': 259200000,  # 72 hours
                    'cleanup.policy': 'compact'
                },
                'validated_data': {
                    'retention.ms': 604800000,  # 7 days
                    'cleanup.policy': 'compact'
                },
                'failed_processing': {
                    'retention.ms': 604800000,  # 7 days
                    'cleanup.policy': 'compact'
                },
                'audit_logs': {
                    'retention.ms': 2592000000,  # 30 days
                    'cleanup.policy': 'delete'
                }
            }
            
            # Create topics with configurations
            new_topics = [
                NewTopic(
                    topic,
                    num_partitions=3,
                    replication_factor=1,
                    config=topic_configs[name]
                )
                for name, topic in self.config.TOPICS.items()
            ]
            
            self.admin_client.create_topics(new_topics)
            logger.info("Kafka topics created successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Kafka pipeline: {str(e)}")
            raise