```python
import pytest
import asyncio
from typing import Dict, Any
import os
from dotenv import load_dotenv
from database.connection import DatabaseConnection
from cache.redis_manager import RedisManager
from security.auth_manager import AuthManager
from security.encryption_manager import EncryptionManager

load_dotenv()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_connection():
    """Create a database connection for testing."""
    connection = DatabaseConnection()
    connection.create_tables()
    yield connection

@pytest.fixture(scope="session")
def redis_client():
    """Create a Redis client for testing."""
    redis_manager = RedisManager()
    yield redis_manager.redis_client

@pytest.fixture
def auth_manager():
    """Create an authentication manager for testing."""
    return AuthManager({
        'secret_key': 'test_secret_key',
        'token_expiry': 3600
    })

@pytest.fixture
def encryption_manager():
    """Create an encryption manager for testing."""
    return EncryptionManager('test_encryption_key')

@pytest.fixture
def mock_profile_data():
    """Create mock profile data for testing."""
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'company': 'Test Company',
        'title': 'Software Engineer',
        'location': 'New York, NY',
        'linkedin_url': 'https://linkedin.com/in/johndoe'
    }

@pytest.fixture
def mock_api_response():
    """Create mock API response data for testing."""
    return {
        'status': 'success',
        'data': {
            'profile': {
                'id': '12345',
                'name': 'John Doe',
                'email': 'john.doe@example.com'
            }
        }
    }
```