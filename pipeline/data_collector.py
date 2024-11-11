from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio
from ..integrations.api_manager import APIManager
from ..scraper.advanced_scraper import AdvancedScraper

logger = logging.getLogger(__name__)

class DataCollector:
    """Collects data from multiple sources including APIs and web scraping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_manager = APIManager(config)
        self.scraper = AdvancedScraper()
    
    async def collect_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from all configured sources."""
        try:
            # Collect data in parallel
            api_data, scraped_data = await asyncio.gather(
                self.api_manager.collect_profile_data(params),
                self._collect_scraped_data(params)
            )
            
            # Combine and structure the data
            return self._structure_collected_data(api_data, scraped_data)
            
        except Exception as e:
            logger.error(f"Data collection error: {str(e)}")
            raise
    
    async def _collect_scraped_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data through web scraping."""
        try:
            urls = self._generate_urls(params)
            scraped_results = []
            
            for url in urls:
                try:
                    result = await self.scraper.scrape(url)
                    scraped_results.append(result)
                except Exception as e:
                    logger.error(f"Scraping error for {url}: {str(e)}")
            
            return self._combine_scraped_data(scraped_results)
            
        except Exception as e:
            logger.error(f"Scraped data collection error: {str(e)}")
            return {}
    
    def _generate_urls(self, params: Dict[str, Any]) -> List[str]:
        """Generate URLs to scrape based on parameters."""
        urls = []
        
        if linkedin_url := params.get('linkedin_url'):
            urls.append(linkedin_url)
        
        if company_domain := params.get('company_domain'):
            urls.append(f"https://{company_domain}")
        
        # Add more URL generation logic as needed
        
        return urls
    
    def _combine_scraped_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine data from multiple scraped sources."""
        combined = {
            'scraped_data': [],
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'source_count': len(results)
            }
        }
        
        for result in results:
            if result and 'content' in result:
                combined['scraped_data'].append({
                    'url': result.get('url', ''),
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {})
                })
        
        return combined
    
    def _structure_collected_data(
        self,
        api_data: Dict[str, Any],
        scraped_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Structure all collected data into a unified format."""
        return {
            'api_data': api_data,
            'scraped_data': scraped_data.get('scraped_data', []),
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'api_sources': api_data.get('metadata', {}).get('sources', []),
                'scraping_sources': scraped_data.get('metadata', {}).get('source_count', 0)
            }
        }