from typing import Dict, Any, List
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class PeopleDataLabsAPI(BaseIntegration):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.peopledatalabs.com/v5"
        self.headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    async def enrich_person(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a person's profile with additional data."""
        endpoint = f"{self.base_url}/person/enrich"
        return await self._make_request(endpoint, params=params)
    
    async def enrich_company(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich company data."""
        endpoint = f"{self.base_url}/company/enrich"
        return await self._make_request(endpoint, params=params)
    
    async def search_people(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for people based on specific criteria."""
        endpoint = f"{self.base_url}/person/search"
        return await self._make_request(endpoint, data=query, method="POST")
    
    async def bulk_enrich(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform bulk enrichment of multiple records."""
        endpoint = f"{self.base_url}/person/bulk_enrich"
        return await self._make_request(endpoint, data={"records": records}, method="POST")
    
    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """Make an API request to People Data Labs."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    endpoint,
                    headers=self.headers,
                    params=params,
                    json=data
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"People Data Labs API error: {str(e)}")
            raise