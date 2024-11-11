import aiohttp
import logging
from typing import Dict, Any, Optional
from .linkedin_api import LinkedInAPI
from .hunter_api import HunterAPI
from .rocketreach_api import RocketReachAPI
from .pdl_api import PeopleDataLabsAPI
from .lexisnexis_api import LexisNexisAPI
from config.api_config import APIConfig

logger = logging.getLogger(__name__)

class APIClient:
    """Unified client for all API integrations."""
    
    def __init__(self):
        config = APIConfig.get_api_configs()
        
        self.linkedin = LinkedInAPI(
            client_id=config['linkedin']['client_id'],
            client_secret=config['linkedin']['client_secret'],
            redirect_uri=config['linkedin']['redirect_uri']
        )
        
        self.hunter = HunterAPI(
            api_key=config['hunter']['api_key']
        )
        
        self.rocketreach = RocketReachAPI(
            api_key=config['rocketreach']['api_key']
        )
        
        self.pdl = PeopleDataLabsAPI(
            api_key=config['pdl']['api_key']
        )
        
        self.lexisnexis = LexisNexisAPI(
            api_key=config['lexisnexis']['api_key']
        )
    
    async def enrich_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich profile data from all available sources."""
        try:
            # Collect data from all sources
            linkedin_data = await self._get_linkedin_data(profile_data)
            hunter_data = await self._get_hunter_data(profile_data)
            rocketreach_data = await self._get_rocketreach_data(profile_data)
            pdl_data = await self._get_pdl_data(profile_data)
            lexisnexis_data = await self._get_lexisnexis_data(profile_data)
            
            # Combine all data
            return self._merge_profile_data(
                profile_data,
                linkedin_data,
                hunter_data,
                rocketreach_data,
                pdl_data,
                lexisnexis_data
            )
            
        except Exception as e:
            logger.error(f"Profile enrichment error: {str(e)}")
            raise
    
    async def _get_linkedin_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get LinkedIn profile data."""
        try:
            if linkedin_url := profile_data.get('linkedin_url'):
                return await self.linkedin.get_profile(linkedin_url)
            return {}
        except Exception as e:
            logger.error(f"LinkedIn data fetch error: {str(e)}")
            return {}
    
    async def _get_hunter_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get Hunter.io data."""
        try:
            results = {}
            if email := profile_data.get('email'):
                verification = await self.hunter.verify_email(email)
                results['email_verification'] = verification
            if domain := profile_data.get('company_domain'):
                domain_data = await self.hunter.domain_search(domain)
                results['company_emails'] = domain_data
            return results
        except Exception as e:
            logger.error(f"Hunter data fetch error: {str(e)}")
            return {}
    
    async def _get_rocketreach_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get RocketReach data."""
        try:
            lookup_params = {
                'name': f"{profile_data.get('first_name', '')} {profile_data.get('last_name', '')}",
                'current_employer': profile_data.get('company'),
                'title': profile_data.get('title')
            }
            return await self.rocketreach.lookup_person(lookup_params)
        except Exception as e:
            logger.error(f"RocketReach data fetch error: {str(e)}")
            return {}
    
    async def _get_pdl_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get People Data Labs data."""
        try:
            enrich_params = {
                'profile': [
                    profile_data.get('linkedin_url'),
                    profile_data.get('email')
                ],
                'min_likelihood': 0.7
            }
            return await self.pdl.enrich_person(enrich_params)
        except Exception as e:
            logger.error(f"PDL data fetch error: {str(e)}")
            return {}
    
    async def _get_lexisnexis_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get LexisNexis data."""
        try:
            return await self.lexisnexis.comprehensive_person_check(profile_data)
        except Exception as e:
            logger.error(f"LexisNexis data fetch error: {str(e)}")
            return {}
    
    def _merge_profile_data(self, original_data: Dict[str, Any], *source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from multiple sources with conflict resolution."""
        merged = original_data.copy()
        merged['enrichment'] = {
            'sources': [],
            'timestamp': datetime.utcnow().isoformat(),
            'data': {}
        }
        
        for source_dict in source_data:
            if source_dict:
                merged['enrichment']['data'].update(source_dict)
                merged['enrichment']['sources'].append(
                    self._determine_source(source_dict)
                )
        
        return merged
    
    def _determine_source(self, data: Dict[str, Any]) -> str:
        """Determine the source of the enrichment data."""
        if 'email_verification' in data:
            return 'hunter.io'
        elif 'profile_id' in data:
            return 'rocketreach'
        elif 'likelihood' in data:
            return 'peopledatalabs'
        elif 'verification_status' in data:
            return 'lexisnexis'
        elif 'id' in data:
            return 'linkedin'
        return 'unknown'