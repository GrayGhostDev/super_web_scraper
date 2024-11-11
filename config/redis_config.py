import os
from typing import Dict, Any

class RedisConfig:
    # Connection settings
    HOST = os.getenv('REDIS_HOST', 'localhost')
    PORT = int(os.getenv('REDIS_PORT', 6379))
    DB = int(os.getenv('REDIS_DB', 0))
    PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Pool settings
    POOL_MAX_CONNECTIONS = int(os.getenv('REDIS_POOL_MAX_CONNECTIONS', 10))
    POOL_TIMEOUT = int(os.getenv('REDIS_POOL_TIMEOUT', 20))
    
    # Cache settings
    DEFAULT_TIMEOUT = int(os.getenv('REDIS_CACHE_TIMEOUT', 300))  # 5 minutes
    KEY_PREFIX = os.getenv('REDIS_KEY_PREFIX', 'grayghost')
    
    @classmethod
    def get_connection_url(cls) -> str:
        """Get Redis connection URL."""
        auth = f":{cls.PASSWORD}@" if cls.PASSWORD else ""
        return f"redis://{auth}{cls.HOST}:{cls.PORT}/{cls.DB}"
    
    @classmethod
    def get_connection_params(cls) -> Dict[str, Any]:
        """Get Redis connection parameters."""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'db': cls.DB,
            'password': cls.PASSWORD,
            'decode_responses': True,
            'max_connections': cls.POOL_MAX_CONNECTIONS,
            'timeout': cls.POOL_TIMEOUT
        }