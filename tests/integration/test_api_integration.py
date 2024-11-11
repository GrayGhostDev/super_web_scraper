```python
import pytest
from integrations.api_client import APIClient
from integrations.linkedin_api import LinkedInAPI
from integrations.hunter_api import HunterAPI
import os

@pytest.mark.integration
class TestAPIIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_client = APIClient()
        self.linkedin_api = LinkedInAPI(
            os.getenv('LINKEDIN_CLIENT_ID'),
            os.getenv('LINKEDIN_CLIENT_SECRET'),
            os.getenv('LINKEDIN_REDIRECT_URI')
        )
        self.hunter_api = HunterAPI(os.getenv('HUNTER_API_KEY'))

    @pytest.mark.asyncio
    async def test_linkedin_profile_fetch(self):
        """Test fetching a LinkedIn profile."""
        profile_url = "https://linkedin.com/in/test-profile"
        result = await self.linkedin_api.get_profile(profile_url)
        
        assert result is not None
        assert 'id' in result
        assert 'first_name' in result
        assert 'last_name' in result

    @pytest.mark.asyncio
    async def test_hunter_email_verification(self):
        """Test email verification with Hunter.io."""
        email = "test@example.com"
        result = await self.hunter_api.verify_email(email)
        
        assert result is not None
        assert 'result' in result

    @pytest.mark.asyncio
    async def test_full_profile_enrichment(self):
        """Test complete profile enrichment flow."""
        profile_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company': 'Test Company'
        }

        result = await self.api_client.enrich_profile(profile_data)
        
        assert result is not None
        assert 'enrichment' in result
        assert len(result['enrichment']['sources']) > 0
```