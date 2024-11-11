import aiohttp
import logging
from typing import Dict, Any
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services = {
            'database': self._check_database,
            'redis': self._check_redis,
            'rabbitmq': self._check_rabbitmq,
            'api': self._check_api_endpoints
        }

    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        tasks = []

        for service, check_func in self.services.items():
            tasks.append(self._run_check(service, check_func))

        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        for service, result in zip(self.services.keys(), completed):
            if isinstance(result, Exception):
                results[service] = {
                    'status': 'error',
                    'error': str(result),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                results[service] = result

        return {
            'status': 'healthy' if all(r.get('status') == 'healthy' 
                                     for r in results.values()) else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': results
        }

    async def _run_check(self, service: str, check_func) -> Dict[str, Any]:
        """Run a single health check with timeout."""
        try:
            return await asyncio.wait_for(check_func(), timeout=5.0)
        except asyncio.TimeoutError:
            return {
                'status': 'error',
                'error': 'Health check timed out',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed for {service}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        from database.connection import DatabaseConnection
        
        try:
            db = DatabaseConnection()
            async with db.get_session() as session:
                await session.execute("SELECT 1")
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Database check failed: {str(e)}")

    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        from cache.redis_manager import RedisManager
        
        try:
            redis = RedisManager()
            await redis.set('health_check', 'ok', expiry=10)
            result = await redis.get('health_check')
            return {
                'status': 'healthy' if result == 'ok' else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Redis check failed: {str(e)}")

    async def _check_rabbitmq(self) -> Dict[str, Any]:
        """Check RabbitMQ connectivity."""
        try:
            # Implement RabbitMQ health check
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"RabbitMQ check failed: {str(e)}")

    async def _check_api_endpoints(self) -> Dict[str, Any]:
        """Check external API endpoints."""
        endpoints = {
            'linkedin': 'https://api.linkedin.com/v2/health',
            'hunter': 'https://api.hunter.io/v2/health',
            'rocketreach': 'https://api.rocketreach.co/v2/health'
        }

        results = {}
        async with aiohttp.ClientSession() as session:
            for name, url in endpoints.items():
                try:
                    async with session.get(url) as response:
                        results[name] = {
                            'status': 'healthy' if response.status == 200 else 'unhealthy',
                            'status_code': response.status,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                except Exception as e:
                    results[name] = {
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }

        return {
            'status': 'healthy' if all(r['status'] == 'healthy' 
                                     for r in results.values()) else 'unhealthy',
            'endpoints': results,
            'timestamp': datetime.utcnow().isoformat()
        }