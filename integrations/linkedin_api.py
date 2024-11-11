import aiohttp
import logging
from typing import Dict, Any, Optional
from .base import BaseIntegration
from datetime import datetime

logger = logging.getLogger(__name__)

class LinkedInAPI(BaseIntegration):
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://api.linkedin.com/v2"
        self.auth_url = "https://www.linkedin.com/oauth/v2"
    
    async def get_auth_url(self, state: str) -> str:
        """Get OAuth2 authorization URL."""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'r_liteprofile r_emailaddress r_organization_social'
        }
        return f"{self.auth_url}/authorization?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    async def get_access_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.auth_url}/accessToken",
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri
                }
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user's LinkedIn profile."""
        headers = {'Authorization': f'Bearer {access_token}'}
        async with aiohttp.ClientSession() as session:
            # Get basic profile
            async with session.get(
                f"{self.base_url}/me",
                headers=headers,
                params={'projection': '(id,firstName,lastName,profilePicture)'}
            ) as response:
                response.raise_for_status()
                profile = await response.json()
            
            # Get email address
            async with session.get(
                f"{self.base_url}/emailAddress",
                headers=headers,
                params={'q': 'members', 'projection': '(elements*(handle~))'}
            ) as response:
                response.raise_for_status()
                email_data = await response.json()
            
            # Combine data
            return {
                'id': profile.get('id'),
                'first_name': profile.get('firstName', {}).get('localized', {}).get('en_US'),
                'last_name': profile.get('lastName', {}).get('localized', {}).get('en_US'),
                'email': email_data.get('elements', [{}])[0].get('handle~', {}).get('emailAddress'),
                'picture_url': profile.get('profilePicture', {}).get('displayImage')
            }
    
    async def get_company_page(self, company_id: str, access_token: str) -> Dict[str, Any]:
        """Get company page information."""
        headers = {'Authorization': f'Bearer {access_token}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/organizations/{company_id}",
                headers=headers
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def search_people(
        self,
        access_token: str,
        keywords: Optional[str] = None,
        company_id: Optional[str] = None,
        start: int = 0,
        count: int = 10
    ) -> Dict[str, Any]:
        """Search for people on LinkedIn."""
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'start': start,
            'count': count,
            'q': 'people'
        }
        
        if keywords:
            params['keywords'] = keywords
        if company_id:
            params['facet.current_company'] = company_id
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/search",
                headers=headers,
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_profile_connections(
        self,
        access_token: str,
        start: int = 0,
        count: int = 50
    ) -> Dict[str, Any]:
        """Get user's connections."""
        headers = {'Authorization': f'Bearer {access_token}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/connections",
                headers=headers,
                params={
                    'start': start,
                    'count': count,
                    'projection': '(elements*(id,firstName,lastName,headline))'
                }
            ) as response:
                response.raise_for_status()
                return await response.json()