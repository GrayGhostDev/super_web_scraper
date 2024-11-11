from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Profile metrics
profiles_enriched = Counter(
    'profiles_enriched_total',
    'Total number of profiles enriched'
)

profile_enrichment_success = Counter( <boltAction type="file" filePath="monitoring/custom_metrics.py">
    'profile_enrichment_success_total',
    'Successfully enriched profiles',
    ['source']
)

profile_enrichment_failure = Counter(
    'profile_enrichment_failure_total',
    'Failed profile enrichments',
    ['source', 'reason']
)

profile_enrichment_duration = Histogram(
    'profile_enrichment_duration_seconds',
    'Time spent enriching profiles',
    ['source']
)

profile_quality_score = Gauge(
    'profile_quality_score',
    'Profile data quality score',
    ['type']
)

# Data source metrics
source_availability = Gauge(
    'data_source_availability',
    'Data source availability status',
    ['source']
)

source_rate_limit = Gauge(
    'data_source_rate_limit_remaining',
    'Remaining rate limit for data source',
    ['source']
)

source_request_quota = Counter(
    'data_source_request_quota_total',
    'API request quota usage',
    ['source']
)

# Business metrics
active_searches = Gauge(
    'active_searches',
    'Number of active profile searches'
)

search_success_rate = Gauge(
    'search_success_rate',
    'Profile search success rate'
)

export_volume = Counter(
    'profile_exports_total',
    'Number of profile exports',
    ['format']
)

class BusinessMetrics:
    @staticmethod
    def record_profile_enrichment(source: str, duration: float, success: bool, failure_reason: str = None):
        """Record profile enrichment metrics."""
        try:
            profiles_enriched.inc()
            profile_enrichment_duration.labels(source=source).observe(duration)
            
            if success:
                profile_enrichment_success.labels(source=source).inc()
            else:
                profile_enrichment_failure.labels(
                    source=source,
                    reason=failure_reason or 'unknown'
                ).inc()
        except Exception as e:
            logger.error(f"Error recording enrichment metrics: {str(e)}")

    @staticmethod
    def update_quality_score(score: float, score_type: str):
        """Update profile quality score."""
        try:
            profile_quality_score.labels(type=score_type).set(score)
        except Exception as e:
            logger.error(f"Error updating quality score: {str(e)}")

    @staticmethod
    def update_source_status(source: str, available: bool, rate_limit: int = None):
        """Update data source status metrics."""
        try:
            source_availability.labels(source=source).set(1 if available else 0)
            if rate_limit is not None:
                source_rate_limit.labels(source=source).set(rate_limit)
        except Exception as e:
            logger.error(f"Error updating source status: {str(e)}")

    @staticmethod
    def record_search_metrics(active_count: int, success_rate: float):
        """Record search-related metrics."""
        try:
            active_searches.set(active_count)
            search_success_rate.set(success_rate)
        except Exception as e:
            logger.error(f"Error recording search metrics: {str(e)}")

    @staticmethod
    def record_export(export_format: str):
        """Record profile export metrics."""
        try:
            export_volume.labels(format=export_format).inc()
        except Exception as e:
            logger.error(f"Error recording export metrics: {str(e)}")