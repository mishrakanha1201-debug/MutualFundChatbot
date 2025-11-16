"""
Intelligent Data Extractor using Gemini LLM
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
try:
    from ..llm.gemini_client import GeminiClient
    from .pdf_scraper import PDFScraper
    from .html_scraper import HTMLScraper
    from .sebi_scraper import SEBIScraper
except ImportError:
    # Fallback for direct execution
    from backend.llm.gemini_client import GeminiClient
    from backend.scraper.pdf_scraper import PDFScraper
    from backend.scraper.html_scraper import HTMLScraper
    from backend.scraper.sebi_scraper import SEBIScraper


class DataExtractor:
    """Orchestrates data extraction from multiple sources with intelligent parsing"""
    
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize data extractor
        
        Args:
            gemini_api_key: Optional Gemini API key
        """
        self.gemini_client = GeminiClient(gemini_api_key)
        self.pdf_scraper = PDFScraper()
        self.html_scraper = HTMLScraper()
        self.sebi_scraper = SEBIScraper()
    
    def extract_from_pdf(self, url: str, source_name: str) -> Dict[str, Any]:
        """
        Extract data from PDF source
        
        Args:
            url: PDF URL
            source_name: Name/type of source
            
        Returns:
            Extracted data dictionary
        """
        logger.info(f"Extracting data from PDF: {url}")
        
        # Scrape PDF
        text_content = self.pdf_scraper.scrape_pdf(url)
        
        if not text_content:
            logger.warning(f"No content extracted from PDF: {url}")
            return {}
        
        # Use Gemini to extract relevant data
        extracted_data = self.gemini_client.extract_relevant_data(text_content, "PDF")
        extracted_data["_source"] = source_name
        extracted_data["_source_url"] = url
        extracted_data["_raw_text_length"] = len(text_content)
        
        return extracted_data
    
    def extract_from_html(self, url: str, source_name: str) -> Dict[str, Any]:
        """
        Extract data from HTML source
        
        Args:
            url: HTML URL
            source_name: Name/type of source
            
        Returns:
            Extracted data dictionary
        """
        logger.info(f"Extracting data from HTML: {url}")
        
        # Scrape HTML
        text_content = self.html_scraper.scrape_url(url)
        
        if not text_content:
            logger.warning(f"No content extracted from HTML: {url}")
            return {}
        
        # Use Gemini to extract relevant data
        extracted_data = self.gemini_client.extract_relevant_data(text_content, "HTML")
        extracted_data["_source"] = source_name
        extracted_data["_source_url"] = url
        extracted_data["_raw_text_length"] = len(text_content)
        
        return extracted_data
    
    def extract_from_sebi(self, url: str) -> Dict[str, Any]:
        """
        Extract data from SEBI source (handles PDF downloads)
        
        Args:
            url: SEBI page URL
            
        Returns:
            Extracted data dictionary
        """
        logger.info(f"Extracting data from SEBI: {url}")
        
        # Scrape SEBI page
        sebi_data = self.sebi_scraper.scrape_sebi_page(url)
        
        # Combine HTML and PDF content
        combined_content = []
        if sebi_data["html_content"]:
            combined_content.append("--- HTML Content ---\n" + sebi_data["html_content"])
        if sebi_data["pdf_content"]:
            combined_content.append(sebi_data["pdf_content"])
        
        if not combined_content:
            logger.warning(f"No content extracted from SEBI: {url}")
            return {}
        
        full_content = "\n\n".join(combined_content)
        
        # Use Gemini to extract relevant data
        extracted_data = self.gemini_client.extract_relevant_data(full_content, "SEBI")
        extracted_data["_source"] = "SEBI"
        extracted_data["_source_url"] = url
        extracted_data["_pdf_urls"] = sebi_data["pdf_urls"]
        extracted_data["_raw_text_length"] = len(full_content)
        
        return extracted_data
    
    def extract_from_all_sources(self, fund_sources: Dict[str, str], fund_name: str) -> Dict[str, Any]:
        """
        Extract data from all sources for a fund and merge results
        
        Args:
            fund_sources: Dictionary mapping source names to URLs
            fund_name: Name of the mutual fund
            
        Returns:
            Merged data dictionary from all sources
        """
        logger.info(f"Extracting data from all sources for: {fund_name}")
        
        all_extracted_data = []
        
        # Process each source
        for source_name, url in fund_sources.items():
            try:
                if "sebi" in source_name.lower():
                    data = self.extract_from_sebi(url)
                elif url.endswith(".pdf") or "pdf" in source_name.lower():
                    data = self.extract_from_pdf(url, source_name)
                else:
                    data = self.extract_from_html(url, source_name)
                
                if data:
                    all_extracted_data.append(data)
                    
            except Exception as e:
                logger.error(f"Error extracting from {source_name} ({url}): {e}")
                continue
        
        # Merge all extracted data
        merged_data = self._merge_extracted_data(all_extracted_data, fund_name)
        
        return merged_data
    
    def _merge_extracted_data(self, data_list: List[Dict[str, Any]], fund_name: str) -> Dict[str, Any]:
        """
        Merge data from multiple sources, prioritizing most complete/accurate values
        
        Args:
            data_list: List of extracted data dictionaries
            fund_name: Name of the fund
            
        Returns:
            Merged data dictionary
        """
        merged = {
            "fund_name": fund_name,
            "sources": [],
            "data": {}
        }
        
        # Collect all unique keys
        all_keys = set()
        for data in data_list:
            all_keys.update(k for k in data.keys() if not k.startswith("_"))
            merged["sources"].append({
                "source": data.get("_source", "unknown"),
                "url": data.get("_source_url", ""),
                "extracted_fields": [k for k in data.keys() if not k.startswith("_")]
            })
        
        # Merge values (prefer non-empty, more specific values)
        for key in all_keys:
            values = []
            for data in data_list:
                if key in data and data[key] is not None:
                    value = data[key]
                    if value != "" and value != "N/A" and value != "Not Available":
                        values.append({
                            "value": value,
                            "source": data.get("_source", "unknown")
                        })
            
            if values:
                # Use the first non-empty value (can be enhanced with priority logic)
                merged["data"][key] = values[0]["value"]
                # Store all values for reference
                if len(values) > 1:
                    merged["data"][f"{key}_alternatives"] = [v["value"] for v in values[1:]]
        
        merged["extraction_timestamp"] = self._get_timestamp()
        merged["total_sources"] = len(data_list)
        
        return merged
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

