from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime
from .stages import (
    DataCollector,
    DataProcessor,
    DataValidator,
    DataEnricher
)

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collector = DataCollector()
        self.processor = DataProcessor()
        self.validator = DataValidator()
        self.enricher = DataEnricher()

    async def process_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through all pipeline stages."""
        try:
            # Stage 1: Collection
            raw_data = await self.collector.collect(params)
            
            # Stage 2: Processing
            processed_data = await self.processor.process(raw_data)
            
            # Stage 3: Validation
            if not await self.validator.validate(processed_data):
                raise ValueError("Data validation failed")
            
            # Stage 4: Enrichment
            enriched_data = await self.enricher.enrich(processed_data)
            
            return {
                'data': enriched_data,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'params': params
                }
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'error',
                    'params': params
                }
            }