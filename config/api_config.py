import os
from typing import Dict, Any

class APIConfig:
    # LinkedIn API settings
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI')
    
    # Hunter API settings
    HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
    
    # RocketReach API settings
    ROCKETREACH_API_KEY = os.getenv('ROCKETREACH_API_KEY')
    
    # People Data Labs API settings
    PDL_API_KEY = os.getenv('PDL_API_KEY')
    
    # LexisNexis API settings
    LEXISNEXIS_API_KEY = os.getenv('LEXISNEXIS_API_KEY')
    
    # Rate limiting settings
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100/hour')
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def get_api_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get all API configurations."""
        return {
            'linkedin': {
                'client_id': cls.LINKEDIN_CLIENT_ID,
                'client_secret': cls.LINKEDIN_CLIENT_SECRET,
                'redirect_uri': cls.LINKEDIN_REDIRECT_URI
            },
            'hunter': {
                'api_key': cls.HUNTER_API_KEY
            },
            'rocketreach': {
                'api_key': cls.ROCKETREACH_API_KEY
            },
            'pdl': {
                'api_key': cls.PDL_API_KEY
            },
            'lexisnexis': {
                'api_key': cls.LEXISNEXIS_API_KEY
            }
        }