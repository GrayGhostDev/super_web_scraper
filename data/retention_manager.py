```python
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram
from database.models import Profile, Company
from sqlalchemy.orm import Session
import asyncio

logger = logging.getLogger(__name__)

# Retention metrics
retention_operations = Counter(
    'retention_operations_total',
    'Data retention operations',
    ['operation', 'status']
)

archival_size = Histogram(
    'archival_size_bytes',
    'Size of archived data',
    ['data_type']
)

class RetentionManager:
    def __init__(self, session: Session):
        self.session = session
        self.retention_policies = {
            'active': {
                'duration': timedelta(days=365),
                'classification': 'active'
            },
            'inactive': {
                'duration': timedelta(days=180),
                'classification': 'archive'
            },
            'deleted': {
                'duration': timedelta(days=90),
                'classification': 'delete'
            }
        }

    async def apply_retention_policies(self):
        """Apply retention policies to all data."""
        try:
            for policy_name, policy in self.retention_policies.items():
                await self._process_policy(policy_name, policy)
                
            retention_operations.labels(
                operation='apply_policies',
                status='success'
            ).inc()
            
        except Exception as e:
            retention_operations.labels(
                operation='apply_policies',
                status='error'
            ).inc()
            logger.error(f"Error applying retention policies: {str(e)}")
            raise

    async def _process_policy(self, policy_name: str, policy: Dict[str, Any]):
        """Process a single retention policy."""
        cutoff_date = datetime.utcnow() - policy['duration']
        
        # Process profiles
        profiles = await self._get_expired_profiles(cutoff_date)
        for profile in profiles:
            await self._handle_expired_data(
                profile,
                policy['classification']
            )

        # Process companies
        companies = await self._get_expired_companies(cutoff_date)
        for company in companies:
            await self._handle_expired_data(
                company,
                policy['classification']
            )

    async def _get_expired_profiles(self, cutoff_date: datetime) -> List[Profile]:
        """Get profiles that have expired based on cutoff date."""
        return self.session.query(Profile).filter(
            Profile.updated_at < cutoff_date
        ).all()

    async def _get_expired_companies(self, cutoff_date: datetime) -> List[Company]:
        """Get companies that have expired based on cutoff date."""
        return self.session.query(Company).filter(
            Company.updated_at < cutoff_date
        ).all()

    async def _handle_expired_data(
        self,
        data: Any,
        classification: str
    ):
        """Handle expired data based on classification."""
        try:
            if classification == 'archive':
                await self._archive_data(data)
            elif classification == 'delete':
                await self._delete_data(data)
            
        except Exception as e:
            logger.error(
                f"Error handling expired data {data.id}: {str(e)}"
            )
            raise

    async def _archive_data(self, data: Any):
        """Archive data to long-term storage."""
        try:
            # Convert to archival format
            archival_data = self._prepare_for_archive(data)
            
            # Store in archival storage
            await self._store_in_archive(archival_data)
            
            # Update data status
            data.status = 'archived'
            await self.session.commit()
            
            retention_operations.labels(
                operation='archive',
                status='success'
            ).inc()
            
        except Exception as e:
            retention_operations.labels(
                operation='archive',
                status='error'
            ).inc()
            raise

    async def _delete_data(self, data: Any):
        """Delete data after retention period."""
        try:
            # Create deletion record
            await self._record_deletion(data)
            
            # Delete from database
            self.session.delete(data)
            await self.session.commit()
            
            retention_operations.labels(
                operation='delete',
                status='success'
            ).inc()
            
        except Exception as e:
            retention_operations.labels(
                operation='delete',
                status='error'
            ).inc()
            raise

    def _prepare_for_archive(self, data: Any) -> Dict[str, Any]:
        """Prepare data for archival storage."""
        return {
            'id': str(data.id),
            'type': data.__class__.__name__,
            'data': data.to_dict(),
            'metadata': {
                'archived_at': datetime.utcnow().isoformat(),
                'retention_policy': 'archive'
            }
        }

    async def _store_in_archive(self, archival_data: Dict[str, Any]):
        """Store data in archival storage."""
        # Implement archival storage logic (e.g., S3 Glacier)
        pass

    async def _record_deletion(self, data: Any):
        """Record data deletion for audit purposes."""
        deletion_record = {
            'entity_id': str(data.id),
            'entity_type': data.__class__.__name__,
            'deletion_date': datetime.utcnow().isoformat(),
            'retention_policy': 'delete'
        }
        # Store deletion record
        pass
```