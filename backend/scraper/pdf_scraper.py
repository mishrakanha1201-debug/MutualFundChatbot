"""
PDF Scraper for AMFI and other PDF sources
"""
import os
import urllib.request
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Try to import PDF libraries, fallback to basic extraction
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    # Use simple PDF extractor as fallback
    from .simple_pdf_extractor import SimplePDFExtractor
    logger.warning("PyPDF2 not available, using basic PDF text extraction")


class PDFScraper:
    """Scraper for extracting text from PDF files"""
    
    def __init__(self, download_dir: str = "downloads"):
        """
        Initialize PDF scraper
        
        Args:
            download_dir: Directory to save downloaded PDFs
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.timeout = int(os.getenv("SCRAPER_TIMEOUT", 30))
        self.delay = float(os.getenv("SCRAPER_DELAY", 2))
    
    def download_pdf(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        Download PDF from URL
        
        Args:
            url: URL of the PDF
            filename: Optional custom filename. If not provided, extracted from URL
            
        Returns:
            Path to downloaded PDF file, or None if download failed
        """
        try:
            if filename is None:
                filename = url.split("/")[-1]
                if not filename.endswith(".pdf"):
                    filename = f"{filename}.pdf"
            
            filepath = self.download_dir / filename
            
            # Skip if already downloaded
            if filepath.exists():
                logger.info(f"PDF already exists: {filepath}")
                return filepath
            
            logger.info(f"Downloading PDF from {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                with open(filepath, "wb") as f:
                    f.write(response.read())
            
            logger.info(f"PDF downloaded successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract all text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return ""
        
        text_content = []
        
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            if HAS_PYPDF2:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        try:
                            text = page.extract_text()
                            if text:
                                text_content.append(f"--- Page {page_num} ---\n{text}\n")
                        except Exception as e:
                            logger.warning(f"Error extracting text from page {page_num}: {e}")
                            continue
            else:
                # Use simple PDF extractor
                logger.info("Using basic PDF text extraction")
                extracted_text = SimplePDFExtractor.extract_text(str(pdf_path))
                if extracted_text and len(extracted_text) > 50:
                    text_content.append(extracted_text)
                else:
                    text_content.append(f"PDF file: {pdf_path.name}")
                    text_content.append("Note: Limited text extraction - some content may be missing")
                    logger.warning("PDF text extraction limited - consider installing PyPDF2 for better results")
            
            full_text = "\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def scrape_pdf(self, url: str, filename: Optional[str] = None) -> str:
        """
        Download and extract text from PDF
        
        Args:
            url: URL of the PDF
            filename: Optional custom filename
            
        Returns:
            Extracted text content
        """
        pdf_path = self.download_pdf(url, filename)
        if pdf_path:
            return self.extract_text_from_pdf(pdf_path)
        return ""

