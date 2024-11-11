```python
import pytest
from cache.redis_manager import RedisManager
import json
from datetime import datetime, timedelta

@pytest.mark.integration
class TestCacheIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, redis_client):
        self.redis = RedisManager()
        self.test_key = "test:cache:key"
        self.test_data = {
            "id": "123",
            "name": "Test Data",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def test_cache_set_get(self):
        """Test setting and getting cached data."""
        # Set data
        success = await self.redis.set(
            self.test_key,
            self.test_data,
            expiry=300
        )
        assert success is True

        # Get data
        cached_data = await self.redis.get(self.test_key)
        assert cached_data is not None
        assert cached_data['id'] == self.test_data['id']
        assert cached_data['name'] == self.test_data['name']

    async def test_cache_expiry(self):
        """Test cache expiration."""
        # Set data with short expiry
        await self.redis.set(
            self.test_key,
            self.test_data,
            expiry=1
        )

        # Wait for expiration
        await asyncio.sleep(2)

        # Try to get expired data
        cached_data = await self.redis.get(self.test_key)
        assert cached_data is None

    async def test_cache_delete(self):
        """Test deleting cached data."""
        # Set data
        await self.redis.set(
            self.test_key,
            self.test_data
        )

        # Delete data
        success = await self.redis.delete(self.test_key)
        assert success is True

        # Verify deletion
        cached_data = await self.redis.get(self.test_key)
        assert cached_data is None

    async def test_cache_exists(self):
        """Test checking existence of cached data."""
        # Check non-existent key
        exists = await self.redis.exists(self.test_key)
        assert exists is False

        # Set data
        await self.redis.set(
            self.test_key,
            self.test_data
        )

        # Check existing key
        exists = await self.redis.exists(self.test_key)
        assert exists is True
```