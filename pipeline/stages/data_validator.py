from typing import Dict, Any, List
import logging
from datetime import datetime
import re
from ...config.settings import PIPELINE_CONFIG

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        self.validation_rules = PIPELINE_CONFIG['validation_rules']
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        self.url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate processed data against defined rules."""
        try:
            validations = [
                await self._validate_required_fields(data),
                await self._validate_data_quality(data),
                await self._validate_data_consistency(data),
                await self._validate_data_format(data)
            ]
            
            return all(validations)
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False
    
    async def _validate_required_fields(self, data: Dict[str, Any]) -> bool:
        """Validate presence and non-emptiness of required fields."""
        try:
            required_fields = self.validation_rules['required_fields']
            
            for field in required_fields:
                if not self._field_exists(data, field) or not self._field_has_value(data, field):
                    logger.warning(f"Required field missing or empty: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Required fields validation error: {str(e)}")
            return False
    
    async def _validate_data_quality(self, data: Dict[str, Any]) -> bool:
        """Validate data quality metrics."""
        try:
            # Validate email format
            if email := self._get_field_value(data, 'email'):
                if not self.email_pattern.match(email):
                    logger.warning(f"Invalid email format: {email}")
                    return False
            
            # Validate phone format
            if phone := self._get_field_value(data, 'phone'):
                if not self.phone_pattern.match(phone):
                    logger.warning(f"Invalid phone format: {phone}")
                    return False
            
            # Validate URL format
            if url := self._get_field_value(data, 'linkedin_url'):
                if not self.url_pattern.match(url):
                    logger.warning(f"Invalid URL format: {url}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data quality validation error: {str(e)}")
            return False
    
    async def _validate_data_consistency(self, data: Dict[str, Any]) -> bool:
        """Validate consistency across related data fields."""
        try:
            # Check date consistency
            if start_date := self._get_field_value(data, 'start_date'):
                if end_date := self._get_field_value(data, 'end_date'):
                    if datetime.fromisoformat(start_date) > datetime.fromisoformat(end_date):
                        logger.warning("Start date is after end date")
                        return False
            
            # Check name consistency
            if full_name := self._get_field_value(data, 'full_name'):
                first_name = self._get_field_value(data, 'first_name')
                last_name = self._get_field_value(data, 'last_name')
                if first_name and last_name:
                    if full_name != f"{first_name} {last_name}":
                        logger.warning("Name fields are inconsistent")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data consistency validation error: {str(e)}")
            return False
    
    async def _validate_data_format(self, data: Dict[str, Any]) -> bool:
        """Validate data format and type consistency."""
        try:
            # Validate date formats
            date_fields = ['start_date', 'end_date', 'birth_date']
            for field in date_fields:
                if value := self._get_field_value(data, field):
                    try:
                        datetime.fromisoformat(value)
                    except ValueError:
                        logger.warning(f"Invalid date format for {field}: {value}")
                        return False
            
            # Validate numeric fields
            numeric_fields = ['confidence_score', 'risk_score']
            for field in numeric_fields:
                if value := self._get_field_value(data, field):
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Invalid numeric format for {field}: {value}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data format validation error: {str(e)}")
            return False
    
    def _field_exists(self, data: Dict[str, Any], field: str) -> bool:
        """Check if a field exists in nested dictionary."""
        if isinstance(data, dict):
            if field in data:
                return True
            return any(self._field_exists(v, field) for v in data.values() if isinstance(v, (dict, list)))
        elif isinstance(data, list):
            return any(self._field_exists(item, field) for item in data)
        return False
    
    def _field_has_value(self, data: Dict[str, Any], field: str) -> bool:
        """Check if a field has a non-empty value."""
        value = self._get_field_value(data, field)
        if value is None:
            return False
        if isinstance(value, (str, list, dict)):
            return bool(value)
        return True
    
    def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get the value of a field from nested dictionary."""
        if isinstance(data, dict):
            if field in data:
                return data[field]
            for v in data.values():
                if isinstance(v, (dict, list)):
                    result = self._get_field_value(v, field)
                    if result is not None:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self._get_field_value(item, field)
                if result is not None:
                    return result
        return None