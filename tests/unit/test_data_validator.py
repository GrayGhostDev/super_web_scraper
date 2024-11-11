```python
import pytest
from pipeline.stages.data_validator import DataValidator
from datetime import datetime

@pytest.fixture
def data_validator():
    return DataValidator()

@pytest.mark.asyncio
async def test_validate_required_fields(data_validator):
    """Test validation of required fields."""
    valid_data = {
        'name': 'John Doe',
        'location': 'New York',
        'skills': ['Python', 'JavaScript']
    }

    invalid_data = {
        'name': 'John Doe',
        'location': ''
    }

    assert await data_validator._validate_required_fields(valid_data) is True
    assert await data_validator._validate_required_fields(invalid_data) is False

@pytest.mark.asyncio
async def test_validate_data_quality(data_validator):
    """Test data quality validation."""
    valid_data = {
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'linkedin_url': 'https://linkedin.com/in/johndoe'
    }

    invalid_data = {
        'email': 'invalid-email',
        'phone': '123',
        'linkedin_url': 'not-a-url'
    }

    assert await data_validator._validate_data_quality(valid_data) is True
    assert await data_validator._validate_data_quality(invalid_data) is False

@pytest.mark.asyncio
async def test_validate_data_consistency(data_validator):
    """Test data consistency validation."""
    valid_data = {
        'start_date': '2020-01-01',
        'end_date': '2021-01-01',
        'full_name': 'John Doe',
        'first_name': 'John',
        'last_name': 'Doe'
    }

    invalid_data = {
        'start_date': '2021-01-01',
        'end_date': '2020-01-01',
        'full_name': 'John Doe',
        'first_name': 'Jane',
        'last_name': 'Doe'
    }

    assert await data_validator._validate_data_consistency(valid_data) is True
    assert await data_validator._validate_data_consistency(invalid_data) is False

@pytest.mark.asyncio
async def test_validate_data_format(data_validator):
    """Test data format validation."""
    valid_data = {
        'start_date': '2021-01-01T00:00:00',
        'confidence_score': 0.95,
        'risk_score': 0.2
    }

    invalid_data = {
        'start_date': 'invalid-date',
        'confidence_score': 'high',
        'risk_score': 'low'
    }

    assert await data_validator._validate_data_format(valid_data) is True
    assert await data_validator._validate_data_format(invalid_data) is False
```