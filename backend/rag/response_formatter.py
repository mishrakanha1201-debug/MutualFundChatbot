"""
Response Formatter - Formats answers according to chatbot constraints
"""
import re
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats responses according to chatbot constraints"""
    
    MAX_SENTENCES = 3
    EDUCATIONAL_LINK = "https://groww.in/p/mutual-funds"
    FACTSHEET_BASE_URL = "https://groww.in/mutual-funds"
    
    def format_answer(self, answer: str, sources: List[Dict[str, Any]], 
                     fund_name: str = None, is_greeting: bool = False) -> Dict[str, Any]:
        """
        Format answer with constraints applied
        
        Args:
            answer: Raw answer from LLM
            sources: List of source chunks used
            fund_name: Optional fund name for citation
            is_greeting: Whether this is a greeting response
            
        Returns:
            Formatted response dictionary
        """
        # Remove performance claims
        answer = self._remove_performance_claims(answer)
        
        # For greetings, don't add citations
        if is_greeting:
            return {
                'answer': answer,
                'citation_link': '',
                'sources': sources,
                'timestamp': None
            }
        
        # Check if answer indicates lack of information/context
        has_no_information = self._indicates_no_information(answer)
        
        # For general finance questions (no sources), don't add citation
        is_general_question = len(sources) == 0 and not has_no_information
        
        # Get citation link only if we have information and it's not a general question
        citation_link = ''
        timestamp = None
        if not has_no_information and not is_general_question:
            citation_link = self._get_citation_link(sources, fund_name)
            timestamp = datetime.now().strftime("%Y-%m-%d")
            # Format final answer with citation (citation added separately, doesn't count)
            formatted_answer = self._add_citation(answer, citation_link, timestamp)
        else:
            # No citation for "no information" answers or general questions
            formatted_answer = answer
        
        return {
            'answer': formatted_answer,
            'citation_link': citation_link,
            'sources': sources,
            'timestamp': timestamp
        }
    
    def _remove_performance_claims(self, text: str) -> str:
        """Remove performance claims and return comparisons"""
        # Patterns to remove or replace
        patterns = [
            (r'returns?\s+(?:of|are|is)\s+[0-9.]+%', ''),
            (r'[0-9.]+%\s+returns?', ''),
            (r'outperforms?', ''),
            (r'better\s+than', ''),
            (r'worse\s+than', ''),
            (r'compare\s+returns?', 'For performance details, please refer to the official factsheet'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _indicates_no_information(self, answer: str) -> bool:
        """
        Check if the answer indicates that no information was found
        
        Args:
            answer: The answer text
            
        Returns:
            True if answer indicates lack of information
        """
        answer_lower = answer.lower()
        
        # Patterns that indicate no information
        no_info_patterns = [
            'does not contain',
            'not available',
            'couldn\'t find',
            'could not find',
            'no information',
            'not in context',
            'not found',
            'unavailable',
            'does not have',
            'doesn\'t have',
            'not present',
            'not provided',
            'cannot find',
            'unable to find',
            'no data',
            'no details',
            'lacks information',
            'missing information',
            'insufficient information',
            'not enough information',
            'apologize.*not.*contain',
            'apologize.*not.*available',
            'apologize.*couldn\'t',
            'apologize.*no information'
        ]
        
        # Check if any pattern matches
        import re
        for pattern in no_info_patterns:
            if re.search(pattern, answer_lower):
                return True
        
        return False
    
    def _limit_sentences(self, text: str, max_sentences: int) -> str:
        """Limit text to maximum number of sentences"""
        # Split by sentence endings, but preserve the punctuation
        # Use a more sophisticated approach
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Add remaining text if any
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Filter empty sentences
        sentences = [s for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        # Take first max_sentences and join
        limited = sentences[:max_sentences]
        result = ' '.join(limited)
        
        # Ensure it ends with punctuation
        if result and not result[-1] in '.!?':
            result += '.'
        
        return result
    
    def _get_citation_link(self, sources: List[Dict[str, Any]], fund_name: str = None) -> str:
        """Get citation link from sources"""
        # Try to get URL from source chunks
        if sources and len(sources) > 0:
            # Check for primary_source_url in metadata
            for source in sources:
                if isinstance(source, dict):
                    # Check if source has metadata with source URLs
                    metadata = source.get('metadata', {})
                    primary_url = metadata.get('primary_source_url')
                    if primary_url and primary_url.startswith('http'):
                        return primary_url
                    
                    # Check for source_urls list
                    source_urls = metadata.get('source_urls', [])
                    if source_urls:
                        # Priority: HDFC > SEBI > AMFI > Groww > any other source
                        for url in source_urls:
                            if isinstance(url, str) and 'hdfcfund.com' in url:
                                return url
                        for url in source_urls:
                            if isinstance(url, str) and 'sebi.gov.in' in url:
                                return url
                        for url in source_urls:
                            if isinstance(url, str) and 'amfiindia.com' in url:
                                return url
                        for url in source_urls:
                            if isinstance(url, str) and 'groww.in' in url:
                                return url
                        # Return first valid URL (any other source)
                        for url in source_urls:
                            if isinstance(url, str) and url.startswith('http'):
                                return url
        
        # Fallback: Try to get from fund_sources.json
        citation_link = self._get_url_from_config(fund_name)
        if citation_link:
            return citation_link
        
        # Final fallback: Generate URL from fund name
        if fund_name:
            fund_slug = fund_name.lower().replace(' ', '-').replace('&', 'and')
            return f"{self.FACTSHEET_BASE_URL}/{fund_slug}"
        
        # Use first source's fund name
        if sources and len(sources) > 0:
            source_fund = sources[0].get('fund_name', '')
            if source_fund:
                fund_slug = source_fund.lower().replace(' ', '-').replace('&', 'and')
                return f"{self.FACTSHEET_BASE_URL}/{fund_slug}"
        
        # Default to general page
        return self.EDUCATIONAL_LINK
    
    def _get_url_from_config(self, fund_name: str = None) -> str:
        """Get URL from fund_sources.json config file"""
        if not fund_name:
            return None
        
        try:
            import json
            from pathlib import Path
            
            config_path = Path("config/fund_sources.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    for fund in config.get('funds', []):
                        if fund.get('name') == fund_name:
                            sources = fund.get('sources', {})
                            # Priority: HDFC > SEBI > AMFI > Groww
                            if 'hdfc' in sources:
                                return sources['hdfc']
                            if 'sebi' in sources:
                                return sources['sebi']
                            if 'amfi_pdf' in sources:
                                return sources['amfi_pdf']
                            if 'groww' in sources:
                                return sources['groww']
        except Exception as e:
            logger.warning(f"Error loading URL from config: {e}")
        
        return None
    
    def _add_citation(self, answer: str, citation_link: str, timestamp: str) -> str:
        """Add citation to answer (citation doesn't count toward sentence limit)"""
        # Count sentences in answer (before adding citation)
        answer_sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
        
        # Ensure answer is ≤3 sentences before adding citation
        if len(answer_sentences) > self.MAX_SENTENCES:
            # Take only first MAX_SENTENCES
            limited_sentences = answer_sentences[:self.MAX_SENTENCES]
            answer = '. '.join(limited_sentences)
            if not answer.endswith(('.', '!', '?')):
                answer += '.'
        
        citation_text = f"Last updated from sources: {timestamp}. For more details, visit: {citation_link}"
        
        # Add citation at the end
        if answer.endswith('.'):
            return f"{answer} {citation_text}"
        else:
            return f"{answer}. {citation_text}"
    
    def format_rejection_message(self, reason: str, query: str) -> Dict[str, Any]:
        """Format rejection message based on reason"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        messages = {
            'pii_detected': {
                'answer': f"I appreciate you reaching out, but I cannot accept personal information like PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers. Please do not share such information. I'm here to help with factual questions about mutual funds.",
                'citation_link': '',  # No citation for rejected queries
                'rejected': True,
                'reason': 'pii_detected',
                'timestamp': None  # No timestamp for rejected queries
            },
            'opinionated': {
                'answer': f"Thank you for your question. I can only provide factual information about mutual funds. I cannot provide investment advice, recommendations, or opinions. For educational resources on mutual fund investing, please visit: {self.EDUCATIONAL_LINK}.",
                'citation_link': '',  # No citation for rejected queries
                'rejected': True,
                'reason': 'opinionated',
                'timestamp': None  # No timestamp for rejected queries
            },
            'not_factual': {
                'answer': f"Thank you for your question. I can help you with factual questions about mutual funds such as expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometer ratings, benchmarks, and how to download statements. Please feel free to ask me about any of these topics.",
                'citation_link': '',  # No citation for rejected queries
                'rejected': True,
                'reason': 'not_factual',
                'timestamp': None  # No timestamp for rejected queries
            }
        }
        
        result = messages.get(reason, {
            'answer': f"I can only answer factual questions about mutual funds.",
            'citation_link': '',  # No citation for rejected queries
            'rejected': True,
            'reason': 'unknown',
            'timestamp': None  # No timestamp for rejected queries
        })
        
        # Ensure rejection messages are also ≤3 sentences
        answer = result['answer']
        sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip() and len(s.strip()) > 10]
        
        if len(sentences) > self.MAX_SENTENCES:
            limited = sentences[:self.MAX_SENTENCES]
            new_main = '. '.join(limited)
            if not new_main.endswith(('.', '!', '?')):
                new_main += '.'
            result['answer'] = new_main
        
        return result

