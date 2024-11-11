```python
import logging
from typing import Dict, Any, List, Optional
from prometheus_client import Counter
from datetime import datetime

logger = logging.getLogger(__name__)

# Access control metrics
access_checks = Counter(
    'access_checks_total',
    'Total access control checks',
    ['result']
)

class AccessControl:
    def __init__(self):
        self.roles = {
            'admin': {
                'permissions': ['read', 'write', 'delete', 'manage'],
                'resources': ['*']
            },
            'user': {
                'permissions': ['read', 'write'],
                'resources': ['profiles', 'searches']
            },
            'viewer': {
                'permissions': ['read'],
                'resources': ['profiles']
            }
        }

    def check_permission(
        self,
        user_role: str,
        resource: str,
        permission: str
    ) -> bool:
        """Check if user has permission for resource."""
        try:
            access_checks.labels(result='checked').inc()
            
            if user_role not in self.roles:
                access_checks.labels(result='denied').inc()
                return False
                
            role_config = self.roles[user_role]
            
            # Check if role has wildcard access
            if '*' in role_config['resources']:
                if permission in role_config['permissions']:
                    access_checks.labels(result='granted').inc()
                    return True
            
            # Check specific resource permission
            if (resource in role_config['resources'] and
                permission in role_config['permissions']):
                access_checks.labels(result='granted').inc()
                return True
                
            access_checks.labels(result='denied').inc()
            return False
            
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            raise

    def get_user_permissions(
        self,
        user_role: str
    ) -> Dict[str, List[str]]:
        """Get all permissions for a user role."""
        try:
            if user_role not in self.roles:
                return {}
                
            return {
                'permissions': self.roles[user_role]['permissions'],
                'resources': self.roles[user_role]['resources']
            }
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            raise

    def add_role(
        self,
        role_name: str,
        permissions: List[str],
        resources: List[str]
    ) -> bool:
        """Add a new role."""
        try:
            if role_name in self.roles:
                return False
                
            self.roles[role_name] = {
                'permissions': permissions,
                'resources': resources
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding role: {str(e)}")
            raise

    def modify_role(
        self,
        role_name: str,
        permissions: Optional[List[str]] = None,
        resources: Optional[List[str]] = None
    ) -> bool:
        """Modify an existing role."""
        try:
            if role_name not in self.roles:
                return False
                
            if permissions is not None:
                self.roles[role_name]['permissions'] = permissions
            if resources is not None:
                self.roles[role_name]['resources'] = resources
                
            return True
            
        except Exception as e:
            logger.error(f"Error modifying role: {str(e)}")
            raise

    def remove_role(self, role_name: str) -> bool:
        """Remove a role."""
        try:
            if role_name not in self.roles:
                return False
                
            del self.roles[role_name]
            return True
            
        except Exception as e:
            logger.error(f"Error removing role: {str(e)}")
            raise
```