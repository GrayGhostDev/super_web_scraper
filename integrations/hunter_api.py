from typing import Dict, Any, Optional
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class HunterAPI(BaseIntegration):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
        
    async def find_email(self, domain: str, full_name: str = None) -> Dict[str, Any]:
        """Find email addresses for a domain or person."""
        params = {
            'api_key': self.api_key,
            'domain': domain
        }
        
        if full_name:
            params['full_name'] = full_name
            
        return await self._make_request(f"{self.base_url}/email-finder", params=params)
    
    async def verify_email(self, email: str) -> Dict[str, Any]:
        """Verify an email address."""
        params = {
            'api_key': self.api_key,
            'email': email
        }
        
        return await self._make_request(f"{self.base_url}/email-verifier", params=params)
    
    async def domain_search(self, domain: str, limit: int = 10) -> Dict[str, Any]:
        """Search for email addresses in a domain."""
        params = {
            'api_key': self.api_key,
            'domain': domain,
            'limit': limit
        }
        
        return await self._make_request(f"{self.base_url}/domain-search", params=params)
    
    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """Make an API request to Hunter.io."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, endpoint, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Hunter.io API error: {str(e)}")
            raise