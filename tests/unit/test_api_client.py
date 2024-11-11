```python
import pytest
from integrations.api_client import APIClient
from unittest.mock import Mock, patch

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.asyncio
async def test_enrich_profile(api_client, mock_profile_data):
    """Test profile enrichment through API client."""
    mock_linkedin_data = {'profile': {'id': '123'}}
    mock_hunter_data = {'email_verification': True}
    mock_rocketreach_data = {'profile_id': '456'}
    mock_pdl_data = {'likelihood': 0.9}

    with patch.object(api_client, '_get_linkedin_data') as mock_linkedin, \
         patch.object(api_client, '_get_hunter_data') as mock_hunter, \
         patch.object(api_client, '_get_rocketreach_data') as mock_rocketreach, \
         patch.object(api_client, '_get_pdl_data') as mock_pdl:
        
        mock_linkedin.return_value = mock_linkedin_data
        mock_hunter.return_value = mock_hunter_data
        mock_rocketreach.return_value = mock_rocketreach_data
        mock_pdl.return_value = mock_pdl_data

        result = await api_client.enrich_profile(mock_profile_data)

        assert result is not None
        assert 'enrichment' in result
        assert len(result['enrichment']['sources']) == 4

@pytest.mark.asyncio
async def test_get_linkedin_data(api_client, mock_profile_data):
    """Test LinkedIn data retrieval."""
    with patch.object(api_client.linkedin, 'get_profile') as mock_get_profile:
        mock_get_profile.return_value = {'id': '123', 'name': 'John Doe'}
        
        result = await api_client._get_linkedin_data(mock_profile_data)
        
        assert result is not None
        assert result['id'] == '123'
        assert result['name'] == 'John Doe'

@pytest.mark.asyncio
async def test_get_hunter_data(api_client, mock_profile_data):
    """Test Hunter.io data retrieval."""
    with patch.object(api_client.hunter, 'verify_email') as mock_verify_email:
        mock_verify_email.return_value = {'result': 'valid'}
        
        result = await api_client._get_hunter_data(mock_profile_data)
        
        assert result is not None
        assert 'email_verification' in result

@pytest.mark.asyncio
async def test_merge_profile_data(api_client):
    """Test merging profile data from multiple sources."""
    original_data = {'name': 'John Doe'}
    source1 = {'email': 'john@example.com'}
    source2 = {'company': 'Test Corp'}

    result = api_client._merge_profile_data(original_data, source1, source2)

    assert result['name'] == 'John Doe'
    assert 'enrichment' in result
    assert len(result['enrichment']['sources']) == 2
```