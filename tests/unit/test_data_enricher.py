```python
import pytest
from pipeline.stages.data_enricher import DataEnricher
from unittest.mock import Mock, patch

@pytest.fixture
def data_enricher():
    return DataEnricher()

@pytest.mark.asyncio
async def test_enrich_profile_success(data_enricher, mock_profile_data):
    """Test successful profile enrichment."""
    # Mock API responses
    mock_linkedin_data = {'profile': {'id': '123', 'name': 'John Doe'}}
    mock_hunter_data = {'email_verification': True}
    mock_pdl_data = {'likelihood': 0.9}

    with patch.object(data_enricher, '_get_linkedin_data') as mock_linkedin, \
         patch.object(data_enricher, '_get_hunter_data') as mock_hunter, \
         patch.object(data_enricher, '_get_pdl_data') as mock_pdl:
        
        mock_linkedin.return_value = mock_linkedin_data
        mock_hunter.return_value = mock_hunter_data
        mock_pdl.return_value = mock_pdl_data

        result = await data_enricher.enrich_profile(mock_profile_data)

        assert result is not None
        assert 'enrichment' in result
        assert len(result['enrichment']['sources']) > 0
        assert result['enrichment']['data'].get('profile') == mock_linkedin_data['profile']

@pytest.mark.asyncio
async def test_enrich_profile_partial_failure(data_enricher, mock_profile_data):
    """Test profile enrichment with some failed sources."""
    mock_linkedin_data = {'profile': {'id': '123', 'name': 'John Doe'}}
    
    with patch.object(data_enricher, '_get_linkedin_data') as mock_linkedin, \
         patch.object(data_enricher, '_get_hunter_data') as mock_hunter, \
         patch.object(data_enricher, '_get_pdl_data') as mock_pdl:
        
        mock_linkedin.return_value = mock_linkedin_data
        mock_hunter.side_effect = Exception("API Error")
        mock_pdl.return_value = {}

        result = await data_enricher.enrich_profile(mock_profile_data)

        assert result is not None
        assert 'enrichment' in result
        assert 'linkedin' in result['enrichment']['sources']
        assert 'hunter.io' not in result['enrichment']['sources']

@pytest.mark.asyncio
async def test_combine_enriched_data(data_enricher):
    """Test combining enriched data from multiple sources."""
    original_data = {'name': 'John Doe'}
    source1 = {'email': 'john@example.com'}
    source2 = {'phone': '123-456-7890'}

    result = data_enricher._combine_enriched_data(original_data, source1, source2)

    assert result['name'] == 'John Doe'
    assert 'enrichment' in result
    assert 'email' in result['enrichment']['data']
    assert 'phone' in result['enrichment']['data']
```