from typing import Dict, Any
import time
import logging
from datetime import datetime
from redis import Redis
from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

# Rate limiting metrics
rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Total number of rate limit hits',
    ['endpoint']
)

current_requests = Gauge(
    'current_requests',
    'Current number of requests',
    ['endpoint']
)

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_limit = 100  # requests per hour
        self.default_window = 3600  # 1 hour in seconds
        
        # Custom limits for different endpoints
        self.limits = {
            'api/search': {'limit': 50, 'window': 3600},
            'api/enrich': {'limit': 200, 'window': 3600},
            'api/verify': {'limit': 100, 'window': 3600}
        }
    
    async def check_rate_limit(self, key: str, endpoint: str) -> bool:
        """Check if request is within rate limits."""
        try:
            limit_config = self.limits.get(endpoint, {'limit': self.default_limit, 'window': self.default_window})
            current_time = int(time.time())
            window_start = current_time - limit_config['window']
            
            # Update request count
            pipeline = self.redis.pipeline()
            pipeline.zremrangebyscore(key, 0, window_start)
            pipeline.zadd(key, {str(current_time): current_time})
            pipeline.zcard(key)
            pipeline.expire(key, limit_config['window'])
            _, _, request_count, _ = pipeline.execute()
            
            # Update metrics
            current_requests.labels(endpoint=endpoint).set(request_count)
            
            if request_count > limit_config['limit']:
                rate_limit_hits.labels(endpoint=endpoint).inc()
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return False
    
    async def get_remaining_requests(self, key: str, endpoint: str) -> Dict[str, Any]:
        """Get remaining requests information."""
        try:
            limit_config = self.limits.get(endpoint, {'limit': self.default_limit, 'window': self.default_window})
            current_time = int(time.time())
            window_start = current_time - limit_config['window']
            
            # Clean up old requests and get current count
            pipeline = self.redis.pipeline()
            pipeline.zremrangebyscore(key, 0, window_start)
            pipeline.zcard(key)
            _, request_count = pipeline.execute()
            
            return {
                'limit': limit_config['limit'],
                'remaining': max(0, limit_config['limit'] - request_count),
                'reset': current_time + limit_config['window']
            }
            
        except Exception as e:
            logger.error(f"Error getting remaining requests: {str(e)}")
            return {
                'limit': 0,
                'remaining': 0,
                'reset': current_time
            }