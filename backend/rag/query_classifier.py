"""
Query Classifier - Determines if query is factual, opinionated, or contains PII
"""
import re
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class QueryClassifier:
    """Classifies user queries to enforce chatbot constraints"""
    
    # Greeting patterns (should be allowed)
    GREETING_PATTERNS = [
        'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon',
        'good evening', 'good night', 'namaste', 'namaskar', 'thanks', 'thank you',
        'bye', 'goodbye', 'see you', 'how are you', 'how do you do'
    ]
    
    # Factual query patterns
    FACTUAL_KEYWORDS = [
        'expense ratio', 'exit load', 'entry load', 'minimum sip', 'sip amount',
        'lock-in', 'lock in', 'riskometer', 'benchmark', 'nav', 'aum',
        'fund manager', 'launch date', 'investment objective', 'category',
        'download', 'statement', 'factsheet', 'what is', 'how to',
        'when', 'where', 'who', 'which', 'details', 'information',
        'description', 'describe', 'overview', 'explain', 'meaning of',
        'capital-gains', 'capital gains', 'statements'
    ]
    
    # General finance/education query patterns (should be allowed)
    GENERAL_FINANCE_KEYWORDS = [
        'what is', 'what are', 'what does', 'what do',
        'explain', 'define', 'definition', 'meaning',
        'how does', 'how do', 'how is', 'how are',
        'tell me about', 'can you explain', 'can you tell me',
        'mutual fund', 'mutual funds', 'expense ratio', 'exit load',
        'sip', 'systematic investment plan', 'lumpsum', 'lump sum',
        'nav', 'net asset value', 'aum', 'assets under management',
        'benchmark', 'riskometer', 'lock-in period', 'lock in period',
        'direct plan', 'regular plan', 'growth option', 'dividend option',
        'equity fund', 'debt fund', 'hybrid fund', 'elss', 'tax saver',
        'large cap', 'mid cap', 'small cap', 'flexi cap', 'multi cap',
        'fund manager', 'amc', 'asset management company', 'sebi', 'amfi',
        'factsheet', 'portfolio', 'diversification', 'volatility', 'returns',
        'investment', 'investing', 'investor', 'redemption', 'switch',
        'stp', 'systematic transfer plan', 'swp', 'systematic withdrawal plan'
    ]
    
    # Opinionated/portfolio query patterns
    OPINIONATED_KEYWORDS = [
        'should i', 'should i buy', 'should i sell', 'should i invest',
        'is it good', 'is it bad', 'is.*good', 'is.*bad', 'good for', 'bad for',
        'recommend', 'advice', 'opinion', 'suggest',
        'best fund', 'worst fund', 'compare returns', 'which is better',
        'performance', 'returns', 'profit', 'loss', 'gain',
        'worth', 'worth it', 'should invest', 'good investment'
    ]
    
    # PII patterns
    PII_PATTERNS = {
        'pan': r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
        'aadhaar': r'\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b',
        'account_number': r'\b\d{9,18}\b',
        'otp': r'\b\d{4,6}\b.*otp|\botp.*\b\d{4,6}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b[6-9]\d{9}\b|\b\+91[6-9]\d{9}\b'
    }
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify query and detect issues
        
        Args:
            query: User's query string
            
        Returns:
            Dictionary with classification results
        """
        query_lower = query.lower()
        
        # Check for PII
        pii_detected = self._detect_pii(query)
        
        # Classify query type
        is_factual = self._is_factual(query_lower)
        is_opinionated = self._is_opinionated(query_lower)
        
        # Determine if query should be answered
        can_answer = is_factual and not is_opinionated and not pii_detected
        
        return {
            'is_factual': is_factual,
            'is_opinionated': is_opinionated,
            'pii_detected': pii_detected,
            'can_answer': can_answer,
            'rejection_reason': self._get_rejection_reason(is_factual, is_opinionated, pii_detected)
        }
    
    def _is_factual(self, query_lower: str) -> bool:
        """Check if query is factual"""
        # Check for greetings first (these are allowed but not strictly factual)
        for greeting in self.GREETING_PATTERNS:
            if greeting in query_lower:
                return True  # Allow greetings to pass through
        
        # Check for general finance/education keywords (these are factual and should be answered)
        for keyword in self.GENERAL_FINANCE_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # Check for factual keywords
        for keyword in self.FACTUAL_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # Check for question words that suggest factual queries
        question_words = ['what', 'when', 'where', 'who', 'which', 'how']
        if any(query_lower.startswith(word) for word in question_words):
            return True
        
        return False
    
    def is_general_finance_question(self, query: str) -> bool:
        """
        Check if query is a general finance/education question (NOT about specific funds)
        
        Args:
            query: User query
            
        Returns:
            True if it's a general finance question (no specific fund mentioned)
        """
        query_lower = query.lower()
        
        # If query mentions a specific fund, it's NOT a general question
        fund_indicators = [
            'hdfc', 'elss', 'flexi cap', 'large and mid cap',
            'fund name', 'scheme', 'specific fund'
        ]
        if any(indicator in query_lower for indicator in fund_indicators):
            return False  # This is about a specific fund, use scraped data
        
        # Patterns that indicate general finance questions (without specific funds)
        general_patterns = [
            'what is', 'what are', 'what does', 'what do',
            'explain', 'define', 'definition', 'meaning',
            'how does', 'how do', 'how is', 'how are',
            'tell me about', 'can you explain', 'can you tell me'
        ]
        
        # Check if query starts with general question patterns
        for pattern in general_patterns:
            if query_lower.startswith(pattern) or pattern in query_lower:
                # Check if it's about finance/mutual funds (but NOT a specific fund)
                finance_terms = [
                    'mutual fund', 'expense ratio', 'exit load', 'sip',
                    'nav', 'aum', 'benchmark', 'riskometer', 'lock-in',
                    'direct plan', 'regular plan', 'equity', 'debt',
                    'fund', 'investment', 'investing', 'portfolio',
                    'amc', 'sebi', 'amfi', 'elss', 'tax saver'
                ]
                if any(term in query_lower for term in finance_terms):
                    # Double-check: if it mentions a fund name, it's not general
                    if not any(fund_ind in query_lower for fund_ind in fund_indicators):
                        return True
        
        return False
    
    def _is_opinionated(self, query_lower: str) -> bool:
        """Check if query is opinionated or asks for advice"""
        # Exclude factual patterns that might match opinionated keywords
        factual_exclusions = [
            'how to download', 'download statements', 'download capital',
            'description of', 'overview of', 'meaning of', 'what is the meaning'
        ]
        
        # If it's a factual pattern, don't mark as opinionated
        for exclusion in factual_exclusions:
            if exclusion in query_lower:
                return False
        
        # Check for keyword matches
        for keyword in self.OPINIONATED_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # Check for comparison patterns
        comparison_patterns = [
            r'which.*better',
            r'which.*best',
            r'which.*worse',
            r'compare.*fund',
            r'better.*than',
            r'worse.*than'
        ]
        
        for pattern in comparison_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _detect_pii(self, query: str) -> Dict[str, Any]:
        """Detect PII in query"""
        detected = {}
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                detected[pii_type] = True
        
        return detected if detected else None
    
    def _get_rejection_reason(self, is_factual: bool, is_opinionated: bool, pii_detected: Any) -> str:
        """Get reason for query rejection"""
        if pii_detected:
            return "pii_detected"
        if is_opinionated:
            return "opinionated"
        if not is_factual:
            return "not_factual"
        return None

