"""
Test script to verify scraper components work correctly
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.scraper.pdf_scraper import PDFScraper
from backend.scraper.html_scraper import HTMLScraper
from backend.scraper.sebi_scraper import SEBIScraper
from backend.llm.gemini_client import GeminiClient
from loguru import logger

def test_components():
    """Test individual components"""
    logger.info("Testing scraper components...")
    
    # Test PDF scraper
    try:
        pdf_scraper = PDFScraper()
        logger.info("✓ PDF scraper initialized")
    except Exception as e:
        logger.error(f"✗ PDF scraper failed: {e}")
        return False
    
    # Test HTML scraper
    try:
        html_scraper = HTMLScraper()
        logger.info("✓ HTML scraper initialized")
    except Exception as e:
        logger.error(f"✗ HTML scraper failed: {e}")
        return False
    
    # Test SEBI scraper
    try:
        sebi_scraper = SEBIScraper()
        logger.info("✓ SEBI scraper initialized")
    except Exception as e:
        logger.error(f"✗ SEBI scraper failed: {e}")
        return False
    
    # Test Gemini client (if API key is set)
    try:
        gemini_client = GeminiClient()
        logger.info("✓ Gemini client initialized")
    except ValueError as e:
        logger.warning(f"⚠ Gemini client not initialized (API key missing): {e}")
    except Exception as e:
        logger.error(f"✗ Gemini client failed: {e}")
        return False
    
    logger.info("All components initialized successfully!")
    return True

if __name__ == "__main__":
    test_components()


