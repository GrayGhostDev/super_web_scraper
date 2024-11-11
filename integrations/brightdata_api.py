from typing import Dict, Any, Optional
import aiohttp
import logging
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class BrightDataAPI(BaseIntegration):
    def __init__(self, customer_id: str, password: str):
        super().__init__()
        self.proxy_url = f"http://{customer_id}:{password}@brd.superproxy.io:22225"
        self.session_config = {
            'proxy': self.proxy_url,
            'timeout': aiohttp.ClientTimeout(total=30)
        }
    
    async def scrape_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Scrape a URL using BrightData proxy."""
        try:
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            headers = {**default_headers, **(headers or {})}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, proxy=self.proxy_url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    
                    return {
                        'url': url,
                        'status_code': response.status,
                        'content': content,
                        'headers': dict(response.headers)
                    }
                    
        except Exception as e:
            logger.error(f"BrightData scraping error: {str(e)}")
            raise
    
    async def scrape_multiple_urls(self, urls: list, headers: Optional[Dict[str, str]] = None) -> list:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_url(url, headers) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)