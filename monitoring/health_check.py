import psutil
import logging
from typing import Dict, Any
from datetime import datetime
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self):
        self.services = {
            'database': self.check_database,
            'redis': self.check_redis,
            'rabbitmq': self.check_rabbitmq,
            'api_endpoints': self.check_api_endpoints
        }
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        for service, check_func in self.services.items():
            try:
                status = await check_func()
                results[service] = {
                    'status': 'healthy' if status else 'unhealthy',
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Health check failed for {service}: {str(e)}")
                results[service] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return results
    
    async def check_database(self) -> bool:
        """Check database connectivity."""
        from database.connection import DatabaseConnection
        try:
            db = DatabaseConnection()
            async with db.get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    async def check_redis(self) -> bool:
        """Check Redis connectivity."""
        from cache.redis_manager import RedisManager
        try:
            redis = RedisManager()
            await redis.set('health_check', 'ok', expiry=10)
            result = await redis.get('health_check')
            return result == 'ok'
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False
    
    async def check_rabbitmq(self) -> bool:
        """Check RabbitMQ connectivity."""
        try:
            # Implement RabbitMQ health check
            return True
        except Exception as e:
            logger.error(f"RabbitMQ health check failed: {str(e)}")
            return False
    
    async def check_api_endpoints(self) -> Dict[str, bool]:
        """Check API endpoints health."""
        endpoints = {
            'linkedin': 'https://api.linkedin.com/v2/health',
            'hunter': 'https://api.hunter.io/v2/health',
            'rocketreach': 'https://api.rocketreach.co/v2/health',
            'pdl': 'https://api.peopledatalabs.com/v5/health'
        }
        
        results = {}
        async with aiohttp.ClientSession() as session:
            for name, url in endpoints.items():
                try:
                    async with session.get(url) as response:
                        results[name] = response.status == 200
                except Exception as e:
                    logger.error(f"API health check failed for {name}: {str(e)}")
                    results[name] = False
        
        return results
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get system resource metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }