```python
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# JWT metrics
token_operations = Counter(
    'token_operations_total',
    'Total token operations',
    ['operation']
)

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new JWT token."""
        try:
            token_operations.labels(operation='create').inc()
            
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)
            
            to_encode.update({
                'exp': expire,
                'iat': datetime.utcnow()
            })
            
            return jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            
        except Exception as e:
            logger.error(f"Token creation error: {str(e)}")
            raise

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            token_operations.labels(operation='verify').inc()
            
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise

    def refresh_token(self, token: str) -> str:
        """Refresh an existing token."""
        try:
            token_operations.labels(operation='refresh').inc()
            
            payload = self.verify_token(token)
            payload.pop('exp', None)
            payload.pop('iat', None)
            
            return self.create_token(
                payload,
                expires_delta=timedelta(days=1)
            )
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise
```