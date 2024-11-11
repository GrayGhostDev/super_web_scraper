from typing import Dict, Any
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class ClearbitAPI(BaseIntegration):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://person.clearbit.com/v2"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def enrich_person(self, email: str) -> Dict[str, Any]:
        """Enrich person data using email."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/people/find",
                    params={'email': email},
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Clearbit person enrichment error: {str(e)}")
            raise
    
    async def enrich_company(self, domain: str) -> Dict[str, Any]:
        """Enrich company data using domain."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://company.clearbit.com/v2/companies/find",
                    params={'domain': domain},
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Clearbit company enrichment error: {str(e)}")
            raise