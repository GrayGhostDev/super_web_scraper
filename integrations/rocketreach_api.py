from typing import Dict, Any, List
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class RocketReachAPI(BaseIntegration):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.rocketreach.co/v2"
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    async def lookup_person(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Look up a person's profile."""
        endpoint = f"{self.base_url}/person/lookup"
        return await self._make_request(endpoint, data=params)
    
    async def search_people(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for people based on criteria."""
        endpoint = f"{self.base_url}/person/search"
        return await self._make_request(endpoint, data=query)
    
    async def lookup_company(self, domain: str) -> Dict[str, Any]:
        """Look up company information."""
        endpoint = f"{self.base_url}/company/lookup"
        return await self._make_request(endpoint, data={"domain": domain})
    
    async def get_contact_details(self, profile_id: str) -> Dict[str, Any]:
        """Get detailed contact information for a profile."""
        endpoint = f"{self.base_url}/person/detail/{profile_id}"
        return await self._make_request(endpoint)
    
    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Make an API request to RocketReach."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    endpoint,
                    headers=self.headers,
                    json=data
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"RocketReach API error: {str(e)}")
            raise