from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio
from ...integrations import (
    LinkedInLeadSync,
    LexisNexisAPI,
    HunterAPI,
    RocketReachAPI,
    PeopleDataLabsAPI
)
from ...config.settings import API_CONFIG

logger = logging.getLogger(__name__)

class DataEnricher:
    def __init__(self):
        self.api_config = API_CONFIG
        self.apis = self._initialize_apis()
    
    def _initialize_apis(self) -> Dict[str, Any]:
        """Initialize API clients."""
        return {
            'linkedin': LinkedInLeadSync(
                self.api_config['linkedin']['access_token'],
                self.api_config['linkedin']['organization_id']
            ),
            'lexisnexis': LexisNexisAPI(
                self.api_config['lexisnexis']['api_key']
            ),
            'hunter': HunterAPI(
                self.api_config['hunter']['api_key']
            ),
            'rocketreach': RocketReachAPI(
                self.api_config['rocketreach']['api_key']
            ),
            'pdl': PeopleDataLabsAPI(
                self.api_config['pdl']['api_key']
            )
        }
    
    async def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data from multiple sources."""
        try:
            enriched_data = data.copy()
            
            # Gather enrichment tasks
            tasks = [
                self._enrich_from_linkedin(data),
                self._enrich_from_lexisnexis(data),
                self._enrich_from_hunter(data),
                self._enrich_from_rocketreach(data),
                self._enrich_from_pdl(data)
            ]
            
            # Execute enrichment tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Enrichment error: {str(result)}")
                    continue
                if result:
                    enriched_data.update(result)
            
            # Add enrichment metadata
            enriched_data['enrichment_metadata'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'sources': [source for source, result in zip(self.apis.keys(), results)
                          if not isinstance(result, Exception) and result],
                'success_rate': len([r for r in results if not isinstance(r, Exception)]) / len(results)
            }
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Data enrichment error: {str(e)}")
            raise
    
    async def _enrich_from_linkedin(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data from LinkedIn."""
        try:
            if linkedin_url := data.get('linkedin_url'):
                profile_data = await self.apis['linkedin'].fetch_profile(linkedin_url)
                return {
                    'linkedin_data': profile_data,
                    'professional_info': self._extract_professional_info(profile_data)
                }
            return {}
        except Exception as e:
            logger.error(f"LinkedIn enrichment error: {str(e)}")
            return {}
    
    async def _enrich_from_lexisnexis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data from LexisNexis."""
        try:
            person_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'address': data.get('location')
            }
            return await self.apis['lexisnexis'].comprehensive_person_check(person_data)
        except Exception as e:
            logger.error(f"LexisNexis enrichment error: {str(e)}")
            return {}
    
    async def _enrich_from_hunter(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data from Hunter.io."""
        try:
            results = {}
            if email := data.get('email'):
                verification = await self.apis['hunter'].verify_email(email)
                results['email_verification'] = verification
            if domain := data.get('company_domain'):
                domain_data = await self.apis['hunter'].domain_search(domain)
                results['company_emails'] = domain_data
            return results
        except Exception as e:
            logger.error(f"Hunter.io enrichment error: {str(e)}")
            return {}
    
    async def _enrich_from_rocketreach(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data from RocketReach."""
        try:
            lookup_params = {
                'name': f"{data.get('first_name', '')} {data.get('last_name', '')}",
                'current_employer': data.get('company'),
                'title': data.get('title')
            }
            return await self.apis['rocketreach'].lookup_person(lookup_params)
        except Exception as e:
            logger.error(f"RocketReach enrichment error: {str(e)}")
            return {}
    
    async def _enrich_from_pdl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data from People Data Labs."""
        try:
            enrich_params = {
                'profile': [
                    data.get('linkedin_url'),
                    data.get('email')
                ],
                'min_likelihood': 0.7
            }
            return await self.apis['pdl'].enrich_person(enrich_params)
        except Exception as e:
            logger.error(f"People Data Labs enrichment error: {str(e)}")
            return {}
    
    def _extract_professional_info(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant professional information from LinkedIn data."""
        return {
            'current_position': profile_data.get('current_position'),
            'experience': profile_data.get('experience', [])[:5],
            'education': profile_data.get('education', [])[:3],
            'skills': profile_data.get('skills', [])[:10],
            'certifications': profile_data.get('certifications', [])[:5]
        }