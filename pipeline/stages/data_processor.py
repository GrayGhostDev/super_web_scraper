from typing import Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    async def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data into standardized format."""
        try:
            processed_data = {
                'api_data': self._process_api_data(raw_data.get('api_data')),
                'web_data': self._process_web_data(raw_data.get('web_data'))
            }
            
            return self._merge_data_sources(processed_data)
            
        except Exception as e:
            logger.error(f"Data processing error: {str(e)}")
            raise
            
    def _process_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API data."""
        if not api_data:
            return {}
            
        try:
            df = pd.DataFrame(api_data.get('results', []))
            if not df.empty:
                df = df.fillna('')
                return df.to_dict('records')
            return {}
            
        except Exception as e:
            logger.error(f"API data processing error: {str(e)}")
            return {}
            
    def _process_web_data(self, web_data: list) -> list:
        """Process web scraped data."""
        if not web_data:
            return []
            
        processed_web_data = []
        for item in web_data:
            try:
                processed_item = {
                    'url': item.get('url', ''),
                    'title': item.get('title', '').strip(),
                    'content': self._clean_content(item.get('content', '')),
                    'links': self._clean_links(item.get('links', []))
                }
                processed_web_data.append(processed_item)
            except Exception as e:
                logger.error(f"Web data processing error: {str(e)}")
                
        return processed_web_data
        
    def _merge_data_sources(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from different sources."""
        return {
            'combined_data': {
                'api_results': processed_data['api_data'],
                'web_results': processed_data['web_data']
            }
        }
        
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        if not content:
            return ''
        return ' '.join(content.split())
        
    def _clean_links(self, links: list) -> list:
        """Clean and validate links."""
        return [link for link in links if link and link.startswith('http')]