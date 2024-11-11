from dataclasses import dataclass

@dataclass
class KafkaConfig:
    """Kafka configuration for the data pipeline"""
    BOOTSTRAP_SERVERS = 'localhost:9092'
    
    # Topic definitions
    TOPICS = {
        'raw_html': 'raw-html-data',
        'extracted_data': 'extracted-profile-data',
        'enriched_data': 'enriched-profile-data',
        'validated_data': 'validated-profile-data',
        'failed_processing': 'failed-processing-data',
        'audit_logs': 'data-pipeline-audit-logs'
    }
    
    # Consumer group IDs
    CONSUMER_GROUPS = {
        'extraction': 'profile-extraction-group',
        'enrichment': 'data-enrichment-group',
        'validation': 'data-validation-group'
    }