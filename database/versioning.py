```python
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

Base = declarative_base()

# Versioning metrics
version_operations = Counter(
    'version_operations_total',
    'Number of versioning operations',
    ['operation']
)

version_size = Histogram(
    'version_size_bytes',
    'Size of version data in bytes',
    ['entity_type']
)

class DataVersion(Base):
    __tablename__ = 'data_versions'

    id = Column(Integer, primary_key=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    comment = Column(String)

class VersionManager:
    def __init__(self, session: Session):
        self.session = session

    async def create_version(
        self,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any],
        created_by: str,
        comment: Optional[str] = None
    ) -> int:
        """Create a new version of an entity."""
        try:
            # Get current version number
            current_version = await self._get_latest_version(entity_type, entity_id)
            new_version = current_version + 1

            # Create version record
            version = DataVersion(
                entity_type=entity_type,
                entity_id=entity_id,
                version=new_version,
                data=data,
                created_by=created_by,
                comment=comment
            )

            self.session.add(version)
            await self.session.commit()

            # Update metrics
            version_operations.labels(operation='create').inc()
            version_size.labels(
                entity_type=entity_type
            ).observe(len(json.dumps(data)))

            return new_version

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Version creation error: {str(e)}")
            raise

    async def get_version(
        self,
        entity_type: str,
        entity_id: str,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a specific version of an entity."""
        try:
            query = self.session.query(DataVersion).filter(
                DataVersion.entity_type == entity_type,
                DataVersion.entity_id == entity_id
            )

            if version is not None:
                query = query.filter(DataVersion.version == version)
            else:
                query = query.order_by(DataVersion.version.desc())

            result = await query.first()
            
            if result:
                version_operations.labels(operation='get').inc()
                return {
                    'version': result.version,
                    'data': result.data,
                    'created_at': result.created_at.isoformat(),
                    'created_by': result.created_by,
                    'comment': result.comment
                }

            return None

        except Exception as e:
            logger.error(f"Version retrieval error: {str(e)}")
            raise

    async def get_version_history(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """Get version history for an entity."""
        try:
            versions = await self.session.query(DataVersion).filter(
                DataVersion.entity_type == entity_type,
                DataVersion.entity_id == entity_id
            ).order_by(DataVersion.version.desc()).all()

            version_operations.labels(operation='history').inc()

            return [{
                'version': v.version,
                'created_at': v.created_at.isoformat(),
                'created_by': v.created_by,
                'comment': v.comment
            } for v in versions]

        except Exception as e:
            logger.error(f"Version history error: {str(e)}")
            raise

    async def compare_versions(
        self,
        entity_type: str,
        entity_id: str,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """Compare two versions of an entity."""
        try:
            v1 = await self.get_version(entity_type, entity_id, version1)
            v2 = await self.get_version(entity_type, entity_id, version2)

            if not v1 or not v2:
                raise ValueError("One or both versions not found")

            version_operations.labels(operation='compare').inc()

            return {
                'version1': version1,
                'version2': version2,
                'differences': self._compare_data(v1['data'], v2['data'])
            }

        except Exception as e:
            logger.error(f"Version comparison error: {str(e)}")
            raise

    async def _get_latest_version(self, entity_type: str, entity_id: str) -> int:
        """Get the latest version number for an entity."""
        try:
            result = await self.session.query(
                DataVersion.version
            ).filter(
                DataVersion.entity_type == entity_type,
                DataVersion.entity_id == entity_id
            ).order_by(
                DataVersion.version.desc()
            ).first()

            return result.version if result else 0

        except Exception as e:
            logger.error(f"Latest version check error: {str(e)}")
            raise

    def _compare_data(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two data dictionaries and return differences."""
        differences = {}

        all_keys = set(data1.keys()) | set(data2.keys())
        for key in all_keys:
            if key not in data1:
                differences[key] = {'type': 'added', 'value': data2[key]}
            elif key not in data2:
                differences[key] = {'type': 'removed', 'value': data1[key]}
            elif data1[key] != data2[key]:
                differences[key] = {
                    'type': 'modified',
                    'old_value': data1[key],
                    'new_value': data2[key]
                }

        return differences
```