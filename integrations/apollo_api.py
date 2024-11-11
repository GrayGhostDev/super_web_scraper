from typing import Dict, Any, List
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class ApolloAPI(BaseIntegration):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def search_people(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for people based on criteria."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/people/search",
                    headers=self.headers,
                    json=query
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Apollo people search error: {str(e)}")
            raise
    
    async def enrich_person(self, email: str) -> Dict[str, Any]:
        """Enrich person data using email."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/people/match",
                    headers=self.headers,
                    json={'email': email}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Apollo person enrichment error: {str(e)}")
            raise
    
    async def get_organization(self, domain: str) -> Dict[str, Any]:
        """Get organization data using domain."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/organizations/match",
                    headers=self.headers,
                    json={'domain': domain}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Apollo organization lookup error: {str(e)}")
            raise