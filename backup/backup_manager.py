```python
import logging
from typing import Dict, Any, Optional, List
import asyncio
import json
import gzip
from datetime import datetime
import boto3
from prometheus_client import Counter, Histogram
import os

logger = logging.getLogger(__name__)

# Backup metrics
backup_operations = Counter(
    'backup_operations_total',
    'Number of backup operations',
    ['operation', 'status']
)

backup_size = Histogram(
    'backup_size_bytes',
    'Size of backup data in bytes',
    ['type']
)

class BackupManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.s3_client = boto3.client('s3')
        self.backup_bucket = config['backup_bucket']
        self.local_backup_dir = config.get('local_backup_dir', 'backups')
        os.makedirs(self.local_backup_dir, exist_ok=True)

    async def create_backup(
        self,
        data: Dict[str, Any],
        backup_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new backup."""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_id = f"{backup_type}_{timestamp}"

            # Prepare backup data
            backup_data = {
                'id': backup_id,
                'type': backup_type,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {},
                'data': data
            }

            # Create local backup
            local_path = await self._create_local_backup(backup_data, backup_id)

            # Upload to S3
            await self._upload_to_s3(local_path, backup_id)

            backup_operations.labels(
                operation='create',
                status='success'
            ).inc()

            return backup_id

        except Exception as e:
            backup_operations.labels(
                operation='create',
                status='error'
            ).inc()
            logger.error(f"Backup creation error: {str(e)}")
            raise

    async def restore_backup(
        self,
        backup_id: str,
        target_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Restore data from a backup."""
        try:
            # Download from S3
            local_path = await self._download_from_s3(backup_id)

            # Read and decompress backup
            backup_data = await self._read_backup(local_path)

            # Restore to target path if specified
            if target_path:
                await self._restore_to_path(backup_data, target_path)

            backup_operations.labels(
                operation='restore',
                status='success'
            ).inc()

            return backup_data

        except Exception as e:
            backup_operations.labels(
                operation='restore',
                status='error'
            ).inc()
            logger.error(f"Backup restoration error: {str(e)}")
            raise

    async def list_backups(
        self,
        backup_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """List available backups with filtering."""
        try:
            # List objects in S3 bucket
            paginator = self.s3_client.get_paginator('list_objects_v2')
            backup_list = []

            async for page in paginator.paginate(Bucket=self.backup_bucket):
                for obj in page.get('Contents', []):
                    backup_info = self._parse_backup_info(obj)
                    
                    if self._matches_filters(
                        backup_info,
                        backup_type,
                        start_date,
                        end_date
                    ):
                        backup_list.append(backup_info)

            backup_operations.labels(
                operation='list',
                status='success'
            ).inc()

            return backup_list

        except Exception as e:
            backup_operations.labels(
                operation='list',
                status='error'
            ).inc()
            logger.error(f"Backup listing error: {str(e)}")
            raise

    async def _create_local_backup(
        self,
        data: Dict[str, Any],
        backup_id: str
    ) -> str:
        """Create a compressed local backup file."""
        backup_path = os.path.join(self.local_backup_dir, f"{backup_id}.gz")
        
        try:
            with gzip.open(backup_path, 'wt') as f:
                json.dump(data, f)

            backup_size.labels(type='local').observe(
                os.path.getsize(backup_path)
            )

            return backup_path

        except Exception as e:
            logger.error(f"Local backup creation error: {str(e)}")
            raise

    async def _upload_to_s3(self, local_path: str, backup_id: str) -> None:
        """Upload backup to S3."""
        try:
            s3_key = f"backups/{backup_id}.gz"
            
            with open(local_path, 'rb') as f:
                self.s3_client.upload_fileobj(f, self.backup_bucket, s3_key)

            backup_size.labels(type='s3').observe(
                os.path.getsize(local_path)
            )

        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise

    async def _download_from_s3(self, backup_id: str) -> str:
        """Download backup from S3."""
        try:
            s3_key = f"backups/{backup_id}.gz"
            local_path = os.path.join(self.local_backup_dir, f"{backup_id}.gz")

            with open(local_path, 'wb') as f:
                self.s3_client.download_fileobj(
                    self.backup_bucket,
                    s3_key,
                    f
                )

            return local_path

        except Exception as e:
            logger.error(f"S3 download error: {str(e)}")
            raise

    async def _read_backup(self, backup_path: str) -> Dict[str, Any]:
        """Read and decompress backup data."""
        try:
            with gzip.open(backup_path, 'rt') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Backup reading error: {str(e)}")
            raise

    def _parse_backup_info(self, s3_object: Dict[str, Any]) -> Dict[str, Any]:
        """Parse backup information from S3 object."""
        key = s3_object['Key']
        backup_id = os.path.splitext(os.path.basename(key))[0]
        
        return {
            'id': backup_id,
            'type': backup_id.split('_')[0],
            'timestamp': s3_object['LastModified'].isoformat(),
            'size': s3_object['Size']
        }

    def _matches_filters(
        self,
        backup_info: Dict[str, Any],
        backup_type: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> bool:
        """Check if backup matches the specified filters."""
        if backup_type and backup_info['type'] != backup_type:
            return False

        timestamp = datetime.fromisoformat(backup_info['timestamp'])
        
        if start_date and timestamp < start_date:
            return False
            
        if end_date and timestamp > end_date:
            return False

        return True
```