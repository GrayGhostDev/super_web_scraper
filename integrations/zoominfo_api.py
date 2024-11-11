from typing import Dict, Any, List
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class ZoomInfoAPI(BaseIntegration):
    def __init__(self, api_key: str, customer_id: str):
        super().__init__()
        self.api_key = api_key
        self.customer_id = customer_id
        self.base_url = "https://api.zoominfo.com/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'X-Customer-Id': customer_id
        }
    
    async def search_companies(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for companies based on criteria."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/companies/search",
                    headers=self.headers,
                    json=query
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"ZoomInfo company search error: {str(e)}")
            raise
    
    async def search_contacts(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for contacts based on criteria."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/contacts/search",
                    headers=self.headers,
                    json=query
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"ZoomInfo contact search error: {str(e)}")
            raise
    
    async def enrich_company(self, domain: str) -> Dict[str, Any]:
        """Enrich company data using domain."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/companies/enrich",
                    headers=self.headers,
                    params={'domain': domain}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"ZoomInfo company enrichment error: {str(e)}")
            raise
    
    async def enrich_contact(self, email: str) -> Dict[str, Any]:
        """Enrich contact data using email."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/contacts/enrich",
                    headers=self.headers,
                    params={'email': email}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"ZoomInfo contact enrichment error: {str(e)}")
            raise