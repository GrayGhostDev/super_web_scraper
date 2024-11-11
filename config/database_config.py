import os
from typing import Dict, Any

class DatabaseConfig:
    # Connection settings
    HOST = os.getenv('POSTGRES_HOST', 'localhost')
    PORT = int(os.getenv('POSTGRES_PORT', 5432))
    DB = os.getenv('POSTGRES_DB', 'grayghost')
    USER = os.getenv('POSTGRES_USER', 'postgres')
    PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    # Pool settings
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
    MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
    POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 1800))
    
    @classmethod
    def get_connection_url(cls) -> str:
        """Get database connection URL."""
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DB}"
    
    @classmethod
    def get_connection_params(cls) -> Dict[str, Any]:
        """Get database connection parameters."""
        return {
            'pool_size': cls.POOL_SIZE,
            'max_overflow': cls.MAX_OVERFLOW,
            'pool_timeout': cls.POOL_TIMEOUT,
            'pool_recycle': cls.POOL_RECYCLE
        }