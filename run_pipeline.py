import asyncio
import logging
from pipeline import KafkaConfig, KafkaPipelineManager, DataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the pipeline"""
    try:
        # Initialize pipeline
        kafka_config = KafkaConfig()
        pipeline_manager = KafkaPipelineManager(kafka_config)
        await pipeline_manager.setup_pipeline()
        
        # Initialize processor
        processor = DataProcessor(kafka_config)
        
        # Run processing tasks
        await asyncio.gather(
            processor.process_raw_html(),
            processor.enrich_profile_data(),
            processor.validate_profile_data()
        )
        
    except Exception as e:
        logger.error(f"Pipeline execution error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())