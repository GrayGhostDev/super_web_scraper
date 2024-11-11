```python
import logging
from typing import Dict, Any, Optional
import aiohttp
import json
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram
import secrets
from cache.redis_manager import RedisManager

logger = logging.getLogger(__name__)

# LinkedIn auth metrics
auth_attempts = Counter(
    'linkedin_auth_attempts_total',
    'Total LinkedIn authentication attempts',
    ['status']
)

auth_latency = Histogram(
    'linkedin_auth_latency_seconds',
    'LinkedIn authentication latency',
    ['operation']
)

class LinkedInAuthManager:
    def __init__(self, config: Dict[str, str], redis_manager: RedisManager):
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.redirect_uri = config['redirect_uri']
        self.scope = [
            'r_liteprofile',
            'r_emailaddress',
            'w_member_social',
            'r_organization_social'
        ]
        self.redis = redis_manager
        self.auth_url = "https://www.linkedin.com/oauth/v2"
        self.api_url = "https://api.linkedin.com/v2"

    async def generate_auth_url(self) -> Dict[str, str]:
        """Generate OAuth2 authorization URL with state."""
        try:
            state = secrets.token_urlsafe(32)
            
            # Store state in Redis for validation
            await self.redis.set(
                f"linkedin_state:{state}",
                {"timestamp": datetime.utcnow().isoformat()},
                expiry=3600  # 1 hour expiry
            )
            
            params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'state': state,
                'scope': ' '.join(self.scope)
            }
            
            auth_url = f"{self.auth_url}/authorization?" + "&".join(
                f"{k}={v}" for k, v in params.items()
            )
            
            return {
                'auth_url': auth_url,
                'state': state
            }
            
        except Exception as e:
            logger.error(f"Error generating auth URL: {str(e)}")
            raise

    async def validate_callback(
        self,
        code: str,
        state: str
    ) -> Optional[Dict[str, Any]]:
        """Validate OAuth callback and exchange code for tokens."""
        try:
            with auth_latency.labels(operation='validate_callback').time():
                # Verify state
                stored_state = await self.redis.get(f"linkedin_state:{state}")
                if not stored_state:
                    auth_attempts.labels(status='invalid_state').inc()
                    logger.error("Invalid or expired state parameter")
                    return None

                # Exchange code for tokens
                tokens = await self._exchange_code(code)
                if not tokens:
                    auth_attempts.labels(status='token_exchange_failed').inc()
                    return None

                # Store tokens
                await self._store_tokens(tokens)
                
                auth_attempts.labels(status='success').inc()
                return tokens
                
        except Exception as e:
            auth_attempts.labels(status='error').inc()
            logger.error(f"Callback validation error: {str(e)}")
            return None

    async def _exchange_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens."""
        try:
            with auth_latency.labels(operation='exchange_code').time():
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
                        if response.status != 200:
                            logger.error(
                                f"Token exchange failed: {response.status}"
                            )
                            return None
                            
                        return await response.json()
                        
        except Exception as e:
            logger.error(f"Code exchange error: {str(e)}")
            return None

    async def _store_tokens(self, tokens: Dict[str, Any]) -> None:
        """Store access tokens in Redis."""
        try:
            expires_in = tokens.get('expires_in', 3600)
            await self.redis.set(
                f"linkedin_tokens:{tokens['access_token']}",
                {
                    'refresh_token': tokens.get('refresh_token'),
                    'expires_at': (
                        datetime.utcnow() + timedelta(seconds=expires_in)
                    ).isoformat()
                },
                expiry=expires_in
            )
        except Exception as e:
            logger.error(f"Token storage error: {str(e)}")
            raise

    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """Refresh expired access token."""
        try:
            with auth_latency.labels(operation='refresh_token').time():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.auth_url}/accessToken",
                        data={
                            'grant_type': 'refresh_token',
                            'refresh_token': refresh_token,
                            'client_id': self.client_id,
                            'client_secret': self.client_secret
                        }
                    ) as response:
                        if response.status != 200:
                            logger.error(
                                f"Token refresh failed: {response.status}"
                            )
                            return None
                            
                        tokens = await response.json()
                        await self._store_tokens(tokens)
                        return tokens
                        
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return None

    async def revoke_access_token(self, access_token: str) -> bool:
        """Revoke access token."""
        try:
            with auth_latency.labels(operation='revoke_token').time():
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.auth_url}/revoke",
                        data={
                            'token': access_token,
                            'client_id': self.client_id,
                            'client_secret': self.client_secret
                        }
                    ) as response:
                        success = response.status == 200
                        if success:
                            await self.redis.delete(
                                f"linkedin_tokens:{access_token}"
                            )
                        return success
                        
        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            return False
```