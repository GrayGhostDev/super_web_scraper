import logging.config
import os
from typing import Dict, Any

def setup_logging() -> None:
    """Configure application logging."""
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'json',
                'level': 'INFO'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'propagate': True
            }
        }
    }
    
    os.makedirs('logs', exist_ok=True)
    logging.config.dictConfig(config)