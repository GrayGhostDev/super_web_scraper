```python
import logging
from typing import Dict, Any, Optional
import aiohttp
import secrets
from datetime import datetime, timedelta
from cache.redis_manager import RedisManager
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# OAuth metrics
oauth_operations = Counter(
    'linkedin_oauth_operations_total',
    'LinkedIn OAuth operations',
    ['operation', 'status']
)

oauth_latency = Histogram(
    'linkedin_oauth_latency_seconds',
    'LinkedIn OAuth operation latency',
    ['operation']
)

class LinkedInOAuth:
    def __init__(self, config: Dict[str, str], redis_manager: RedisManager):
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.redirect_uri = config['redirect_uri']
        self.redis = redis_manager
        self.auth_url = "https://www.linkedin.com/oauth/v2"
        self.api_url = "https://api.linkedin.com/v2"
        self.scope = [
            'r_liteprofile',
            'r_emailaddress',
            'w_member_social',
            'r_organization_social'
        ]

    async def generate_auth_url(self) -> Dict[str, str]:
        """Generate OAuth2 authorization URL with state."""
        try:
            with oauth_latency.labels(operation='generate_url').time():
                state = secrets.token_urlsafe(32)
                
                # Store state in Redis for validation
                await self.redis.set(
                    f"linkedin_oauth_state:{state}",
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'used': False
                    },
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
                
                oauth_operations.labels(
                    operation='generate_url',
                    status='success'
                ).inc()
                
                return {
                    'auth_url': auth_url,
                    'state': state
                }
                
        except Exception as e:
            oauth_operations.labels(
                operation='generate_url',
                status='error'
            ).inc()
            logger.error(f"Error generating auth URL: {str(e)}")
            raise

    async def handle_callback(
        self,
        code: str,
        state: str
    ) -> Optional[Dict[str, Any]]:
        """Handle OAuth callback and exchange code for tokens."""
        try:
            with oauth_latency.labels(operation='handle_callback').time():
                # Verify state
                stored_state = await self.redis.get(
                    f"linkedin_oauth_state:{state}"
                )
                
                if not stored_state or stored_state.get('used'):
                    oauth_operations.labels(
                        operation='verify_state',
                        status='error'
                    ).inc()
                    logger.error("Invalid or used state parameter")
                    return None

                # Mark state as used
                stored_state['used'] = True
                await self.redis.set(
                    f"linkedin_oauth_state:{state}",
                    stored_state,
                    expiry=3600
                )

                # Exchange code for tokens
                tokens = await self._exchange_code(code)
                if not tokens:
                    return None

                # Store tokens
                await self._store_tokens(tokens)
                
                oauth_operations.labels(
                    operation='handle_callback',
                    status='success'
                ).inc()
                
                return tokens
                
        except Exception as e:
            oauth_operations.labels(
                operation='handle_callback',
                status='error'
            ).inc()
            logger.error(f"Callback handling error: {str(e)}")
            return None

    async def _exchange_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens."""
        try:
            with oauth_latency.labels(operation='exchange_code').time():
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
                            oauth_operations.labels(
                                operation='exchange_code',
                                status='error'
                            ).inc()
                            logger.error(
                                f"Token exchange failed: {response.status}"
                            )
                            return None
                            
                        oauth_operations.labels(
                            operation='exchange_code',
                            status='success'
                        ).inc()
                        
                        return await response.json()
                        
        except Exception as e:
            oauth_operations.labels(
                operation='exchange_code',
                status='error'
            ).inc()
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
            
            oauth_operations.labels(
                operation='store_tokens',
                status='success'
            ).inc()
            
        except Exception as e:
            oauth_operations.labels(
                operation='store_tokens',
                status='error'
            ).inc()
            logger.error(f"Token storage error: {str(e)}")
            raise

    async def refresh_token(
        self,
        refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """Refresh expired access token."""
        try:
            with oauth_latency.labels(operation='refresh_token').time():
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
                            oauth_operations.labels(
                                operation='refresh_token',
                                status='error'
                            ).inc()
                            logger.error(
                                f"Token refresh failed: {response.status}"
                            )
                            return None
                            
                        tokens = await response.json()
                        await self._store_tokens(tokens)
                        
                        oauth_operations.labels(
                            operation='refresh_token',
                            status='success'
                        ).inc()
                        
                        return tokens
                        
        except Exception as e:
            oauth_operations.labels(
                operation='refresh_token',
                status='error'
            ).inc()
            logger.error(f"Token refresh error: {str(e)}")
            return None
```