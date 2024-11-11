```python
import bcrypt
import logging
from typing import Tuple
import re
from prometheus_client import Counter, Histogram
import time

logger = logging.getLogger(__name__)

# Password metrics
password_operations = Counter(
    'password_operations_total',
    'Total password operations',
    ['operation']
)

password_strength = Histogram(
    'password_strength_score',
    'Password strength scores',
    ['range']
)

class PasswordManager:
    def __init__(self, min_length: int = 8):
        self.min_length = min_length
        self.password_pattern = re.compile(
            r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        )

    def hash_password(self, password: str) -> bytes:
        """Hash a password using bcrypt."""
        try:
            password_operations.labels(operation='hash').inc()
            
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode(), salt)
            
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise

    def verify_password(self, password: str, hashed_password: bytes) -> bool:
        """Verify a password against its hash."""
        try:
            password_operations.labels(operation='verify').inc()
            
            return bcrypt.checkpw(
                password.encode(),
                hashed_password
            )
            
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            raise

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength and requirements."""
        try:
            if len(password) < self.min_length:
                return False, f"Password must be at least {self.min_length} characters long"

            if not self.password_pattern.match(password):
                return False, "Password must contain at least one letter, one number, and one special character"

            strength = self._calculate_password_strength(password)
            password_strength.labels(
                range=f"{(strength // 20) * 20}-{((strength // 20) + 1) * 20}"
            ).observe(strength)

            return True, "Password meets requirements"
            
        except Exception as e:
            logger.error(f"Password validation error: {str(e)}")
            raise

    def _calculate_password_strength(self, password: str) -> float:
        """Calculate password strength score (0-100)."""
        score = 0
        
        # Length
        score += min(len(password) * 4, 40)
        
        # Character variety
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[@$!%*#?&]', password):
            score += 10
        
        # Complexity
        if len(set(password)) > len(password) * 0.5:
            score += 20
            
        return min(score, 100)
```