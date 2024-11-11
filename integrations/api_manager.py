from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime
from .linkedin_sync import LinkedInLeadSync
from .lexisnexis_api import LexisNexisAPI
from .hunter_api import HunterAPI
from .rocketreach_api import RocketReachAPI
from .pdl_api import PeopleDataLabsAPI
from .brightdata_api import BrightDataAPI
from .clearbit_api import ClearbitAPI
from .apollo_api import ApolloAPI
from .zoominfo_api import ZoomInfoAPI

logger = logging.getLogger(__name__)

class APIManager:
    """Manages all API integrations and coordinates data collection."""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.apis = self._initialize_apis()
        
    def _initialize_apis(self) -> Dict[str, Any]:
        """Initialize all API clients."""
        return {
            'linkedin': LinkedInLeadSync(
                self.config['linkedin_access_token'],
                self.config['linkedin_org_id']
            ),
            'lexisnexis': LexisNexisAPI(
                self.config['lexisnexis_api_key']
            ),
            'hunter': HunterAPI(
                self.config['hunter_api_key']
            ),
            'rocketreach': RocketReachAPI(
                self.config['rocketreach_api_key']
            ),
            'pdl': PeopleDataLabsAPI(
                self.config['pdl_api_key']
            ),
            'brightdata': BrightDataAPI(
                self.config['brightdata_customer_id'],
                self.config['brightdata_password']
            ),
            'clearbit': ClearbitAPI(
                self.config['clearbit_api_key']
            ),
            'apollo': ApolloAPI(
                self.config['apollo_api_key']
            ),
            'zoominfo': ZoomInfoAPI(
                self.config['zoominfo_api_key'],
                self.config['zoominfo_customer_id']
            )
        }
    
    async def collect_profile_data(self, profile_params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect profile data from all available sources."""
        tasks = [
            self._collect_linkedin_data(profile_params),
            self._collect_contact_data(profile_params),
            self._collect_company_data(profile_params),
            self._collect_enrichment_data(profile_params)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return self._combine_results(results)
    
    async def _collect_linkedin_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from LinkedIn."""
        try:
            if linkedin_url := params.get('linkedin_url'):
                return await self.apis['linkedin'].fetch_profile(linkedin_url)
            return {}
        except Exception as e:
            logger.error(f"LinkedIn data collection error: {str(e)}")
            return {}
    
    async def _collect_contact_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect contact information from multiple sources."""
        try:
            tasks = [
                self.apis['hunter'].verify_email(params.get('email')) if params.get('email') else None,
                self.apis['rocketreach'].lookup_person(params),
                self.apis['apollo'].search_people({'email': params.get('email')}) if params.get('email') else None
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self._combine_contact_data(results)
        except Exception as e:
            logger.error(f"Contact data collection error: {str(e)}")
            return {}
    
    async def _collect_company_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect company information from multiple sources."""
        try:
            if company_domain := params.get('company_domain'):
                tasks = [
                    self.apis['clearbit'].enrich_company(company_domain),
                    self.apis['zoominfo'].enrich_company(company_domain)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return self._combine_company_data(results)
            return {}
        except Exception as e:
            logger.error(f"Company data collection error: {str(e)}")
            return {}
    
    async def _collect_enrichment_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect enrichment data from multiple sources."""
        try:
            tasks = [
                self.apis['pdl'].enrich_person(params),
                self.apis['lexisnexis'].comprehensive_person_check(params)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self._combine_enrichment_data(results)
        except Exception as e:
            logger.error(f"Enrichment data collection error: {str(e)}")
            return {}
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from all data sources."""
        combined_data = {
            'profile_data': {},
            'contact_data': {},
            'company_data': {},
            'enrichment_data': {},
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'sources': []
            }
        }
        
        for result in results:
            if isinstance(result, dict):
                if 'profile' in result:
                    combined_data['profile_data'].update(result['profile'])
                if 'contact' in result:
                    combined_data['contact_data'].update(result['contact'])
                if 'company' in result:
                    combined_data['company_data'].update(result['company'])
                if 'enrichment' in result:
                    combined_data['enrichment_data'].update(result['enrichment'])
                if 'source' in result:
                    combined_data['metadata']['sources'].append(result['source'])
        
        return combined_data
    
    def _combine_contact_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine contact data from multiple sources."""
        combined = {'contact': {}, 'source': 'contact_apis'}
        
        for result in results:
            if isinstance(result, dict):
                combined['contact'].update(result)
        
        return combined
    
    def _combine_company_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine company data from multiple sources."""
        combined = {'company': {}, 'source': 'company_apis'}
        
        for result in results:
            if isinstance(result, dict):
                combined['company'].update(result)
        
        return combined
    
    def _combine_enrichment_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine enrichment data from multiple sources."""
        combined = {'enrichment': {}, 'source': 'enrichment_apis'}
        
        for result in results:
            if isinstance(result, dict):
                combined['enrichment'].update(result)
        
        return combined