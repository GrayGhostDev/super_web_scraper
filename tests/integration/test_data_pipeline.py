```python
import pytest
from pipeline.data_pipeline import DataPipeline
from pipeline.kafka_config import KafkaConfig
from unittest.mock import Mock

@pytest.fixture
def pipeline():
    config = {
        'kafka': KafkaConfig(),
        'api_keys': {
            'linkedin': 'test_key',
            'hunter': 'test_key',
            'pdl': 'test_key'
        }
    }
    return DataPipeline(config)

@pytest.mark.asyncio
async def test_full_pipeline_flow(pipeline, mock_profile_data):
    """Test complete pipeline flow from collection to validation."""
    # Process data through pipeline
    result = await pipeline.process_data({
        'profile_url': 'https://linkedin.com/in/test',
        'enrich': True
    })

    assert result is not None
    assert 'data' in result
    assert 'metadata' in result
    assert result['metadata']['status'] == 'success'

@pytest.mark.asyncio
async def test_pipeline_error_handling(pipeline):
    """Test pipeline error handling."""
    # Test with invalid input
    result = await pipeline.process_data({
        'profile_url': 'invalid-url'
    })

    assert result is not None
    assert 'error' in result
    assert result['metadata']['status'] == 'error'

@pytest.mark.asyncio
async def test_pipeline_data_validation(pipeline, mock_profile_data):
    """Test data validation in pipeline."""
    # Process valid data
    valid_result = await pipeline.process_data({
        'profile': mock_profile_data
    })

    assert valid_result['metadata']['status'] == 'success'

    # Process invalid data
    invalid_result = await pipeline.process_data({
        'profile': {'name': 'Test'}  # Missing required fields
    })

    assert invalid_result['metadata']['status'] == 'error'
```