import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_CONFIG: Dict[str, Any] = {
    'lexisnexis': {
        'base_url': 'https://api.lexisnexis.com/v1',
        'api_key': os.getenv('LEXISNEXIS_API_KEY'),
        'timeout': 30,
        'retry_attempts': 3
    },
    'scraping': {
        'max_concurrent': 4,
        'timeout': 20,
        'user_agent': 'Gray Ghost Data Generator/1.0'
    }
}

# Pipeline Configuration
PIPELINE_CONFIG: Dict[str, Any] = {
    'stages': ['collection', 'processing', 'validation', 'enrichment'],
    'validation_rules': {
        'required_fields': ['name', 'location', 'skills'],
        'min_confidence_score': 0.7
    },
    'update_interval': int(os.getenv('UPDATE_INTERVAL', '10')),
    'max_workers': int(os.getenv('MAX_WORKERS', '4'))
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'application.log',
            'formatter': 'standard'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': os.getenv('LOG_LEVEL', 'INFO')
        }
    }
}