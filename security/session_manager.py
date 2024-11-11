```python
import redis
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from prometheus_client import Counter, Gauge
import uuid

logger = logging.getLogger(__name__)

# Session metrics
session_operations = Counter(
    'session_operations_total',
    'Total session operations',
    ['operation']
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

class SessionManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_prefix = "session:"
        self.default_expiry = timedelta(hours=24)

    async def create_session(
        self,
        user_id: str,
        data: Dict[str, Any] = None,
        expiry: Optional[timedelta] = None
    ) -> str:
        """Create a new session."""
        try:
            session_operations.labels(operation='create').inc()
            
            session_id = str(uuid.uuid4())
            session_key = f"{self.session_prefix}{session_id}"
            
            session_data = {
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'data': data or {},
                'last_accessed': datetime.utcnow().isoformat()
            }
            
            await self.redis.setex(
                session_key,
                expiry or self.default_expiry,
                json.dumps(session_data)
            )
            
            active_sessions.inc()
            return session_id
            
        except Exception as e:
            logger.error(f"Session creation error: {str(e)}")
            raise

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        try:
            session_operations.labels(operation='get').inc()
            
            session_key = f"{self.session_prefix}{session_id}"
            session_data = await self.redis.get(session_key)
            
            if not session_data:
                return None
                
            session = json.loads(session_data)
            session['last_accessed'] = datetime.utcnow().isoformat()
            
            await self.redis.setex(
                session_key,
                self.default_expiry,
                json.dumps(session)
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Session retrieval error: {str(e)}")
            raise

    async def update_session(
        self,
        session_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Update session data."""
        try:
            session_operations.labels(operation='update').inc()
            
            session = await self.get_session(session_id)
            if not session:
                return False
                
            session['data'].update(data)
            session['last_accessed'] = datetime.utcnow().isoformat()
            
            session_key = f"{self.session_prefix}{session_id}"
            await self.redis.setex(
                session_key,
                self.default_expiry,
                json.dumps(session)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Session update error: {str(e)}")
            raise

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            session_operations.labels(operation='delete').inc()
            
            session_key = f"{self.session_prefix}{session_id}"
            result = await self.redis.delete(session_key)
            
            if result:
                active_sessions.dec()
                
            return bool(result)
            
        except Exception as e:
            logger.error(f"Session deletion error: {str(e)}")
            raise

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        try:
            session_operations.labels(operation='cleanup').inc()
            
            pattern = f"{self.session_prefix}*"
            expired_count = 0
            
            async for key in self.redis.scan_iter(pattern):
                if not await self.redis.exists(key):
                    expired_count += 1
                    active_sessions.dec()
                    
            return expired_count
            
        except Exception as e:
            logger.error(f"Session cleanup error: {str(e)}")
            raise
```