"""
SEBI Website Scraper - Handles PDF downloads from SEBI portal
"""
import os
import time
import urllib.request
import re
from typing import Optional, Dict, Any
from pathlib import Path
import logging
from .pdf_scraper import PDFScraper
from .html_scraper import SimpleHTMLParser

logger = logging.getLogger(__name__)


class SEBIScraper:
    """Scraper for SEBI mutual fund information portal"""
    
    def __init__(self, download_dir: str = "downloads"):
        """
        Initialize SEBI scraper
        
        Args:
            download_dir: Directory to save downloaded PDFs
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.timeout = int(os.getenv("SCRAPER_TIMEOUT", 30))
        self.delay = float(os.getenv("SCRAPER_DELAY", 2))
        self.pdf_scraper = PDFScraper(download_dir)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    def find_pdf_links(self, html_content: str) -> list:
        """
        Find all PDF links in the HTML content
        
        Args:
            html_content: HTML content from SEBI page
            
        Returns:
            List of PDF URLs
        """
        pdf_links = []
        
        # Use regex to find PDF links
        # Look for href="..." or src="..." containing .pdf
        patterns = [
            r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
            r'src=["\']([^"\']*\.pdf[^"\']*)["\']',
            r'["\']([^"\']*\.pdf[^"\']*)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                href = match
                if href.endswith('.pdf') or 'pdf' in href.lower():
                    # Handle relative URLs
                    if href.startswith('/'):
                        href = f"https://www.sebi.gov.in{href}"
                    elif not href.startswith('http'):
                        href = f"https://www.sebi.gov.in/{href}"
                    pdf_links.append(href)
        
        return list(set(pdf_links))  # Remove duplicates
    
    def scrape_sebi_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape SEBI page and extract content, including downloading PDFs
        
        Args:
            url: SEBI page URL
            
        Returns:
            Dictionary with HTML content and PDF content
        """
        result = {
            "html_content": "",
            "pdf_content": "",
            "pdf_urls": []
        }
        
        try:
            logger.info(f"Scraping SEBI page: {url}")
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
            
            result["html_content"] = html_content
            
            # Extract text from HTML using simple parser
            parser = SimpleHTMLParser()
            parser.feed(html_content)
            text_content = parser.get_text()
            result["html_content"] = text_content
            
            # Find and download PDFs
            pdf_urls = self.find_pdf_links(html_content)
            result["pdf_urls"] = pdf_urls
            
            if pdf_urls:
                logger.info(f"Found {len(pdf_urls)} PDF(s) on SEBI page")
                pdf_texts = []
                
                for pdf_url in pdf_urls:
                    try:
                        logger.info(f"Downloading PDF from SEBI: {pdf_url}")
                        # Extract filename from URL
                        filename = pdf_url.split("/")[-1]
                        if not filename.endswith(".pdf"):
                            filename = f"sebi_{filename}.pdf"
                        
                        pdf_path = self.pdf_scraper.download_pdf(pdf_url, filename)
                        if pdf_path:
                            pdf_text = self.pdf_scraper.extract_text_from_pdf(pdf_path)
                            if pdf_text:
                                pdf_texts.append(pdf_text)
                        
                        time.sleep(self.delay)  # Be respectful with requests
                        
                    except Exception as e:
                        logger.error(f"Error downloading PDF {pdf_url}: {e}")
                        continue
                
                result["pdf_content"] = "\n\n--- PDF Content ---\n\n".join(pdf_texts)
            
            logger.info("SEBI page scraped successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping SEBI page {url}: {e}")
            return result

