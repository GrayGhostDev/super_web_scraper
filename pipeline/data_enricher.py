from typing import Dict, Any, List
import logging
from datetime import datetime
from ..integrations import (
    HunterAPI,
    RocketReachAPI,
    PeopleDataLabsAPI,
    LexisNexisAPI
)

logger = logging.getLogger(__name__)

class DataEnricher:
    def __init__(self, config: Dict[str, str]):
        self.hunter_api = HunterAPI(config['hunter_api_key'])
        self.rocketreach_api = RocketReachAPI(config['rocketreach_api_key'])
        self.pdl_api = PeopleDataLabsAPI(config['pdl_api_key'])
        self.lexisnexis_api = LexisNexisAPI(config['lexisnexis_api_key'])
    
    async def enrich_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich profile data using multiple data sources."""
        try:
            # Gather enrichment data from all sources
            hunter_data = await self._get_hunter_data(profile_data)
            rocketreach_data = await self._get_rocketreach_data(profile_data)
            pdl_data = await self._get_pdl_data(profile_data)
            lexisnexis_data = await self._get_lexisnexis_data(profile_data)
            
            # Combine and validate enriched data
            enriched_data = self._combine_enriched_data(
                profile_data,
                hunter_data,
                rocketreach_data,
                pdl_data,
                lexisnexis_data
            )
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Profile enrichment error: {str(e)}")
            raise
    
    async def _get_hunter_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from Hunter.io."""
        try:
            if profile.get('email'):
                verification = await self.hunter_api.verify_email(profile['email'])
                return {'email_verification': verification}
            elif profile.get('domain'):
                domain_search = await self.hunter_api.domain_search(profile['domain'])
                return {'domain_data': domain_search}
            return {}
        except Exception as e:
            logger.warning(f"Hunter.io data fetch error: {str(e)}")
            return {}
    
    async def _get_rocketreach_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from RocketReach."""
        try:
            lookup_params = {
                'name': f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                'current_employer': profile.get('company'),
                'title': profile.get('title')
            }
            return await self.rocketreach_api.lookup_person(lookup_params)
        except Exception as e:
            logger.warning(f"RocketReach data fetch error: {str(e)}")
            return {}
    
    async def _get_pdl_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from People Data Labs."""
        try:
            enrich_params = {
                'profile': [
                    profile.get('linkedin_url'),
                    profile.get('email')
                ],
                'min_likelihood': 0.7
            }
            return await self.pdl_api.enrich_person(enrich_params)
        except Exception as e:
            logger.warning(f"People Data Labs data fetch error: {str(e)}")
            return {}
    
    async def _get_lexisnexis_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from LexisNexis."""
        try:
            return await self.lexisnexis_api.comprehensive_person_check({
                'id': profile.get('id'),
                'first_name': profile.get('first_name'),
                'last_name': profile.get('last_name'),
                'address': profile.get('location')
            })
        except Exception as e:
            logger.warning(f"LexisNexis data fetch error: {str(e)}")
            return {}
    
    def _combine_enriched_data(self, original_data: Dict[str, Any], *source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine data from multiple sources with conflict resolution."""
        enriched = original_data.copy()
        enriched['enrichment'] = {
            'sources': [],
            'timestamp': datetime.utcnow().isoformat(),
            'data': {}
        }
        
        for source_dict in source_data:
            if source_dict:
                enriched['enrichment']['data'].update(source_dict)
                enriched['enrichment']['sources'].append(
                    self._determine_source(source_dict)
                )
        
        return enriched
    
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
        return 'unknown'