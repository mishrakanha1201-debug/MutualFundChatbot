"""
Simple PDF text extractor using standard library
This is a basic implementation that extracts text from PDFs without external libraries
"""
import re
import zlib
from typing import Optional


class SimplePDFExtractor:
    """Basic PDF text extractor using standard library only"""
    
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        Extract text from PDF file using basic parsing
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
            
            # Extract text using regex patterns for PDF text objects
            text_parts = []
            
            # Pattern 1: Extract text from BT...ET blocks (text objects)
            # Format: BT ... (text) Tj ... ET
            bt_et_pattern = rb'BT\s*(.*?)\s*ET'
            matches = re.findall(bt_et_pattern, pdf_content, re.DOTALL)
            
            for match in matches:
                # Extract text within parentheses - more specific pattern
                # Look for (text) Tj or (text) ' patterns
                text_matches = re.findall(rb'\(([^)]+)\)\s*T[jJ]', match)
                text_matches += re.findall(rb'\(([^)]+)\)\s*\'', match)
                
                for text_match in text_matches:
                    try:
                        # Skip if it looks like binary data (too many non-ASCII)
                        if len(text_match) > 1000:  # Skip very long matches (likely binary)
                            continue
                        
                        # Try to decode as text
                        text = text_match.decode('utf-8', errors='ignore')
                        if not text:
                            text = text_match.decode('latin-1', errors='ignore')
                        
                        # Check if it's mostly readable text
                        if len(text) < 3:
                            continue
                        
                        # Count ASCII/printable characters
                        ascii_count = sum(1 for c in text if ord(c) < 128 and (c.isalnum() or c.isspace() or c in '.,;:!?()-'))
                        if ascii_count < len(text) * 0.6:  # Less than 60% readable
                            continue
                        
                        # Clean up escape sequences
                        text = text.replace('\\n', '\n').replace('\\r', '\r')
                        text = text.replace('\\t', '\t')
                        # Remove PDF escape sequences but keep readable text
                        text = re.sub(r'\\([0-9]{1,3})', lambda m: chr(int(m.group(1))) if int(m.group(1)) < 128 else '', text)
                        text = re.sub(r'\\(.)', r'\1', text)
                        
                        # Final cleanup
                        text = ''.join(c for c in text if c.isprintable() or c.isspace())
                        text = text.strip()
                        
                        if text and len(text) > 2:
                            text_parts.append(text)
                    except:
                        continue
            
            # Pattern 2: Extract text from stream objects (more selective)
            stream_pattern = rb'/FlateDecode.*?stream\s*(.*?)\s*endstream'
            stream_matches = re.findall(stream_pattern, pdf_content, re.DOTALL)
            
            for stream in stream_matches[:5]:  # Limit to first 5 streams to avoid binary data
                try:
                    # Try to decompress if compressed
                    try:
                        decompressed = zlib.decompress(stream)
                    except:
                        continue  # Skip if can't decompress
                    
                    # Look for text patterns in decompressed stream
                    # More specific: look for (text) Tj patterns
                    text_matches = re.findall(rb'\(([^)]{2,200})\)\s*T[jJ]', decompressed)
                    
                    for text_match in text_matches:
                        try:
                            # Decode and validate
                            text = text_match.decode('utf-8', errors='ignore')
                            if not text or len(text) < 3:
                                continue
                            
                            # Must be mostly readable
                            ascii_count = sum(1 for c in text if ord(c) < 128 and (c.isalnum() or c.isspace() or c in '.,;:!?()-'))
                            if ascii_count < len(text) * 0.7:
                                continue
                            
                            text = text.strip()
                            if text:
                                text_parts.append(text)
                        except:
                            continue
                except:
                    continue
            
            # Combine all text parts
            full_text = '\n'.join(text_parts)
            
            # Clean up: remove excessive whitespace and non-printable chars
            lines = []
            for line in full_text.split('\n'):
                line = line.strip()
                # Filter out lines that are mostly non-printable or too short
                if line and len(line) > 2:
                    # Count printable characters
                    printable_count = sum(1 for c in line if c.isprintable() or c.isspace())
                    if printable_count > len(line) * 0.7:  # At least 70% printable
                        # Remove control characters except newlines and tabs
                        cleaned = ''.join(c for c in line if c.isprintable() or c in '\n\t')
                        if cleaned.strip():
                            lines.append(cleaned)
            
            result = '\n'.join(lines)
            
            # Additional cleanup: remove very short lines that are likely artifacts
            final_lines = []
            for line in result.split('\n'):
                line = line.strip()
                # Keep lines that are meaningful (length > 3 or contain letters)
                if len(line) > 3 or any(c.isalpha() for c in line):
                    final_lines.append(line)
            
            return '\n'.join(final_lines)
            
        except Exception as e:
            return f"Error extracting PDF: {e}"

