"""
Main script to run the mutual fund scraper
"""
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.scraper.data_extractor import DataExtractor
from backend.database.storage import DataStorage


def setup_logging():
    """Configure logging"""
    # Already configured in module level
    pass


def load_fund_config() -> dict:
    """Load fund sources configuration"""
    config_path = Path(__file__).parent.parent / "config" / "fund_sources.json"
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading fund config: {e}")
        raise


def main():
    """Main scraper execution"""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Starting Mutual Fund Data Scraper")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_fund_config()
    funds = config.get("funds", [])
    
    if not funds:
        logger.error("No funds configured in fund_sources.json")
        return
    
    # Initialize components
    extractor = DataExtractor()
    storage = DataStorage()
    
    all_funds_data = []
    
    # Process each fund
    for fund_config in funds:
        fund_name = fund_config["name"]
        sources = fund_config["sources"]
        
        logger.info("")
        logger.info(f"Processing: {fund_name}")
        logger.info("-" * 60)
        
        try:
            # Extract data from all sources
            fund_data = extractor.extract_from_all_sources(sources, fund_name)
            
            if fund_data and fund_data.get("data"):
                # Save individual fund data
                storage.save_fund_data(fund_data, fund_name)
                all_funds_data.append(fund_data)
                
                # Log summary
                logger.info(f"✓ Successfully extracted data for {fund_name}")
                logger.info(f"  - Sources processed: {fund_data.get('total_sources', 0)}")
                logger.info(f"  - Data points extracted: {len(fund_data.get('data', {}))}")
                
                # Show some key data points
                data = fund_data.get("data", {})
                key_fields = ["expense_ratio", "exit_load", "minimum_sip", "lock_in_period", 
                             "riskometer", "benchmark", "nav", "aum"]
                found_fields = [f for f in key_fields if f in data]
                if found_fields:
                    logger.info(f"  - Key fields found: {', '.join(found_fields)}")
            else:
                logger.warning(f"✗ No data extracted for {fund_name}")
                
        except Exception as e:
            logger.error(f"✗ Error processing {fund_name}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            continue
    
    # Save consolidated data
    if all_funds_data:
        storage.save_consolidated_data(all_funds_data)
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"Scraping completed successfully!")
        logger.info(f"Total funds processed: {len(all_funds_data)}")
        logger.info(f"Data saved to: {storage.data_dir}")
        logger.info("=" * 60)
    else:
        logger.error("No data was extracted from any fund")


if __name__ == "__main__":
    main()

