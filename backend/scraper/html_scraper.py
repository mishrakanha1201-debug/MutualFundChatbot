"""
HTML Scraper for Groww and HDFC websites
"""
import os
import time
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HTMLScraper:
    """Scraper for HTML content from websites like Groww and HDFC"""
    
    def __init__(self):
        """Initialize HTML scraper"""
        self.timeout = int(os.getenv("SCRAPER_TIMEOUT", 30))
        self.delay = float(os.getenv("SCRAPER_DELAY", 2))
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    
    def scrape_url(self, url: str) -> str:
        """
        Scrape HTML content from URL and extract text
        
        Args:
            url: URL to scrape
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Scraping HTML from: {url}")
            
            # Create request with headers
            req = urllib.request.Request(url, headers=self.headers)
            
            # Open URL
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
            
            # Use simple HTML parser to extract text
            parser = SimpleHTMLParser()
            parser.feed(html_content)
            text_content = parser.get_text()
            
            # Clean up excessive whitespace
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            logger.info(f"Extracted {len(cleaned_text)} characters from HTML")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error scraping HTML from {url}: {e}")
            return ""


class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract text content"""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {'script', 'style', 'noscript', 'nav', 'footer', 'header', 'aside'}
        self.in_skip = False
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        if tag.lower() in self.skip_tags:
            self.in_skip = True
    
    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags:
            self.in_skip = False
        if tag.lower() in ('p', 'div', 'br', 'li'):
            self.text_parts.append('\n')
        self.current_tag = None
    
    def handle_data(self, data):
        if not self.in_skip and data.strip():
            self.text_parts.append(data.strip())
    
    def get_text(self):
        return ' '.join(self.text_parts)

