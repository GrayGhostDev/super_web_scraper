```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging
from typing import Dict, Any
from prometheus_client import Histogram

logger = logging.getLogger(__name__)

# Encryption metrics
encryption_duration = Histogram(
    'encryption_duration_seconds',
    'Time spent on encryption operations',
    ['operation']
)

class EncryptionManager:
    def __init__(self, key: str = None):
        self.key = key or os.getenv('ENCRYPTION_KEY')
        if not self.key:
            self.key = self._generate_key()
        self.fernet = Fernet(self._ensure_bytes(self.key))

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            with encryption_duration.labels(operation='encrypt').time():
                encrypted = self.fernet.encrypt(self._ensure_bytes(data))
                return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt encrypted data."""
        try:
            with encryption_duration.labels(operation='decrypt').time():
                decoded = base64.urlsafe_b64decode(encrypted_data)
                decrypted = self.fernet.decrypt(decoded)
                return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise

    def _generate_key(self) -> str:
        """Generate a new encryption key."""
        try:
            key = Fernet.generate_key()
            return base64.urlsafe_b64encode(key).decode()
        except Exception as e:
            logger.error(f"Key generation error: {str(e)}")
            raise

    def _ensure_bytes(self, data: str) -> bytes:
        """Ensure data is in bytes format."""
        return data.encode() if isinstance(data, str) else data

    def rotate_key(self) -> str:
        """Rotate encryption key."""
        try:
            new_key = self._generate_key()
            new_fernet = Fernet(self._ensure_bytes(new_key))
            self.fernet = new_fernet
            self.key = new_key
            return new_key
        except Exception as e:
            logger.error(f"Key rotation error: {str(e)}")
            raise
```