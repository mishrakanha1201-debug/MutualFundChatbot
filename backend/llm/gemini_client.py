"""
Google Gemini API Client for intelligent data extraction
"""
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import time
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Load .env manually
def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in .env file")
        
        # Use gemini-2.0-flash-lite (recommended by Google, cost-efficient and low latency)
        # This is the current recommended model (gemini-1.5-flash was deprecated)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"
        self.max_retries = 3
        self.retry_delay_base = 2  # Base delay in seconds for exponential backoff
        logger.info(f"Gemini client initialized with model: gemini-2.0-flash-lite")
    
    def _make_api_request_with_retry(self, prompt: str, max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Make API request with retry logic for rate limiting (429 errors)
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retries (defaults to self.max_retries)
            
        Returns:
            API response as dictionary
            
        Raises:
            urllib.error.HTTPError: If request fails after all retries
        """
        max_retries = max_retries or self.max_retries
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        json_data = json.dumps(data).encode('utf-8')
        api_url = f"{self.api_url}?key={self.api_key}"
        
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(
                    api_url,
                    data=json_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result
                    
            except urllib.error.HTTPError as e:
                error_detail = str(e)
                error_body = ""
                
                # Try to parse error response
                try:
                    error_body = e.read().decode('utf-8')
                    error_json = json.loads(error_body)
                    error_detail = error_json.get('error', {}).get('message', error_detail)
                except Exception:
                    pass
                
                # Handle rate limiting (429) with retry
                if e.code == 429:
                    if attempt < max_retries:
                        # Exponential backoff: 2^attempt seconds
                        wait_time = self.retry_delay_base * (2 ** attempt)
                        logger.warning(f"Rate limit hit (429). Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        # All retries exhausted
                        logger.error(f"Rate limit exceeded after {max_retries} retries: {error_detail}")
                        raise urllib.error.HTTPError(
                            e.url, e.code,
                            f"Resource exhausted. API rate limit exceeded. Please try again later. {error_detail}",
                            e.headers, e.fp
                        )
                else:
                    # For other HTTP errors, don't retry
                    logger.error(f"Gemini API HTTP Error {e.code}: {error_detail}")
                    raise
                    
            except Exception as e:
                if attempt < max_retries:
                    wait_time = self.retry_delay_base * (2 ** attempt)
                    logger.warning(f"API request failed. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API request failed after {max_retries} retries: {e}")
                    raise
    
    def extract_relevant_data(self, text_content: str, source_type: str) -> Dict[str, Any]:
        """
        Use Gemini to intelligently extract relevant data points from scraped content
        
        Args:
            text_content: Raw text content from source
            source_type: Type of source (pdf, html, etc.)
            
        Returns:
            Dictionary of extracted data points
        """
        prompt = f"""You are an expert at analyzing mutual fund documents. Extract all relevant and informative data points from the following content.

The content is from a {source_type} source about a mutual fund scheme.

Extract the following information if available:
- Expense ratio
- Exit load
- Minimum SIP amount
- Lock-in period (especially for ELSS funds)
- Riskometer rating
- Benchmark index
- Statement download procedures
- NAV (Net Asset Value)
- AUM (Assets Under Management)
- Fund manager name
- Launch date
- Investment objective
- Fund category
- Any other relevant information that would be useful for investors

IMPORTANT: 
1. Extract ALL relevant data points, not just the ones listed above
2. If a data point is not available, do not include it
3. Return the data as a JSON object with clear, descriptive keys
4. Be precise with numbers and percentages
5. Include any additional informative fields you find

Content to analyze:
{text_content[:8000]}  # Limit to avoid token limits

Return ONLY a valid JSON object, no additional text."""

        try:
            # Make API request with retry logic
            result = self._make_api_request_with_retry(prompt)
            
            # Extract text from response
            if 'candidates' in result and len(result['candidates']) > 0:
                response_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                logger.error("No response from Gemini API")
                return {}
            
            # Clean response - remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            extracted_data = json.loads(response_text)
            logger.info(f"Successfully extracted {len(extracted_data)} data points using Gemini")
            return extracted_data
            
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.error(f"Rate limit exceeded in data extraction: {e}")
            else:
                logger.error(f"HTTP error in Gemini extraction: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error in Gemini extraction: {e}")
            return {}
    
    def identify_data_relevance(self, text_chunk: str) -> bool:
        """
        Determine if a text chunk contains relevant mutual fund information
        
        Args:
            text_chunk: Text to analyze
            
        Returns:
            True if relevant, False otherwise
        """
        prompt = f"""Determine if the following text contains relevant information about mutual funds that would be useful for investors.

Relevant information includes:
- Fund details (expense ratio, exit load, NAV, AUM)
- Investment terms (minimum SIP, lock-in period)
- Risk information (riskometer, risk factors)
- Performance metrics
- Fund manager information
- Investment objectives
- Statement/download procedures
- Any other investor-relevant information

Text to analyze:
{text_chunk[:2000]}

Respond with only "YES" or "NO"."""

        try:
            # Make API request with retry logic
            result = self._make_api_request_with_retry(prompt)
            
            # Extract text from response
            if 'candidates' in result and len(result['candidates']) > 0:
                result_text = result['candidates'][0]['content']['parts'][0]['text'].strip().upper()
                return result_text == "YES"
            return True  # Default to relevant
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.error(f"Rate limit exceeded in relevance check: {e}")
            else:
                logger.error(f"HTTP error in relevance check: {e}")
            return True  # Default to relevant if check fails
        except Exception as e:
            logger.error(f"Error in relevance check: {e}")
            return True  # Default to relevant if check fails

