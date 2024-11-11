import logging
from functools import wraps
from typing import Callable, Any
from .auth_manager import AuthManager
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for routes."""
    @wraps(f)
    async def decorated(*args, **kwargs) -> Any:
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'error': 'No authorization header'}, 401

            token = auth_header.split(' ')[1]
            auth_manager = AuthManager()
            if not await auth_manager.verify_token(token):
                return {'error': 'Invalid token'}, 401

            return await f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {'error': 'Authentication failed'}, 401

    return decorated

def rate_limit(limit: str = "100/hour") -> Callable:
    """Decorator to apply rate limiting to routes."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def decorated(*args, **kwargs) -> Any:
            try:
                rate_limiter = RateLimiter()
                key = f"{request.remote_addr}:{f.__name__}"
                
                if not await rate_limiter.check_rate_limit(key, limit):
                    return {'error': 'Rate limit exceeded'}, 429

                return await f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Rate limiting error: {str(e)}")
                return {'error': 'Rate limiting failed'}, 500

        return decorated
    return decorator