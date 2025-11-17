"""
RAG Pipeline - Main orchestrator for Retrieval-Augmented Generation
"""
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .document_processor import DocumentProcessor
from .embedding_store import EmbeddingStore
from .query_classifier import QueryClassifier
from .response_formatter import ResponseFormatter
from ..llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Main RAG pipeline for question answering"""
    
    def __init__(self, data_dir: str = "data/scraped", embeddings_dir: str = "data/embeddings"):
        """
        Initialize RAG pipeline
        
        Args:
            data_dir: Directory containing scraped fund data
            embeddings_dir: Directory for storing embeddings
        """
        self.data_dir = Path(data_dir)
        self.document_processor = DocumentProcessor()
        self.embedding_store = EmbeddingStore(storage_dir=embeddings_dir)
        self.gemini_client = GeminiClient()
        self.query_classifier = QueryClassifier()
        self.response_formatter = ResponseFormatter()
        
        self.chunks = []
        self._initialize_chunks()
    
    def _initialize_chunks(self):
        """Load and process documents into chunks"""
        logger.info("Initializing RAG pipeline with fund data...")
        
        # Process all funds into chunks
        self.chunks = self.document_processor.process_all_funds(self.data_dir)
        
        # Generate embeddings for all chunks
        logger.info(f"Generating embeddings for {len(self.chunks)} chunks...")
        texts = [chunk['text'] for chunk in self.chunks]
        embeddings = self.embedding_store.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(self.chunks, embeddings):
            chunk['embedding'] = embedding
        
        logger.info(f"RAG pipeline initialized with {len(self.chunks)} chunks")
    
    def query(self, question: str, fund_name: Optional[str] = None, top_k: int = 3) -> Dict[str, Any]:
        """
        Answer a question using RAG pipeline with constraints
        
        Args:
            question: User's question
            fund_name: Optional specific fund to search in
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing query: {question}")
        
        # Check if it's a greeting first (before classification)
        query_lower = question.lower().strip()
        greeting_keywords = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 
                            'good evening', 'good night', 'namaste', 'namaskar', 'thanks', 'thank you', 
                            'bye', 'goodbye', 'see you', 'how are you', 'how do you do']
        is_greeting = any(greeting in query_lower for greeting in greeting_keywords)
        
        # Handle greetings directly
        if is_greeting:
            logger.info("Detected greeting, generating friendly response")
            # Let LLM handle greetings with a simple context
            answer = self._generate_answer(question, "This is a greeting or general conversation. Respond politely and offer help.")
            formatted = self.response_formatter.format_answer(
                answer,
                [],
                fund_name,
                is_greeting=True
            )
            return {
                'answer': formatted['answer'],
                'sources': [],
                'confidence': 0.5,
                'citation_link': formatted.get('citation_link', ''),
                'timestamp': formatted.get('timestamp')
            }
        
        # Classify query and check constraints
        classification = self.query_classifier.classify_query(question)
        
        # Check if it's a general finance question
        is_general_finance = self.query_classifier.is_general_finance_question(question)
        
        # If query should be rejected, return rejection message
        if not classification['can_answer']:
            rejection = self.response_formatter.format_rejection_message(
                classification['rejection_reason'],
                question
            )
            return {
                'answer': rejection['answer'],
                'sources': [],
                'confidence': 0.0,
                'rejected': True,
                'rejection_reason': rejection['reason'],
                'citation_link': rejection['citation_link'],
                'timestamp': rejection.get('timestamp')
            }
        
        # Handle general finance questions (answer using LLM's general knowledge)
        if is_general_finance:
            logger.info("Detected general finance question, using LLM general knowledge")
            answer = self._generate_general_finance_answer(question)
            formatted = self.response_formatter.format_answer(
                answer,
                [],
                fund_name,
                is_greeting=False
            )
            return {
                'answer': formatted['answer'],
                'sources': [],
                'confidence': 0.7,  # Medium confidence for general knowledge
                'citation_link': formatted.get('citation_link', ''),
                'timestamp': formatted.get('timestamp')
            }
        
        # Extract fund name from query if not provided
        if not fund_name:
            fund_name = self._extract_fund_name_from_query(question)
        
        # Filter chunks by fund if specified
        search_chunks = self.chunks
        if fund_name:
            # Try exact match first
            search_chunks = [c for c in self.chunks 
                           if fund_name.lower() in c['metadata'].get('fund_name', '').lower()]
            # If no exact match, try partial match (e.g., "HDFC ELSS Fund" matches "HDFC ELSS Tax Saver Fund")
            if not search_chunks:
                search_chunks = [c for c in self.chunks 
                               if self._fuzzy_fund_match(fund_name, c['metadata'].get('fund_name', ''))]
            if not search_chunks:
                logger.warning(f"No chunks found for fund: {fund_name}, searching all chunks")
                search_chunks = self.chunks
        
        # Generate query embedding
        query_embedding = self.embedding_store.generate_embedding(question)
        
        # Find similar chunks using hybrid search (semantic + keyword boost)
        similar_chunks = self._hybrid_search(
            question, query_embedding, search_chunks, top_k=top_k
        )
        
        if not similar_chunks:
            return {
                'answer': "I couldn't find relevant information to answer your question. Please ensure your question is about factual information like expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometer ratings, benchmarks, or how to download statements. How else can I help you?",
                'sources': [],
                'confidence': 0.0,
                'citation_link': self.response_formatter.EDUCATIONAL_LINK
            }
        
        # Prepare context from retrieved chunks
        context_parts = []
        for result in similar_chunks:
            chunk = result['chunk']
            similarity = result['similarity']
            metadata = chunk.get('metadata', {})
            context_parts.append({
                'text': chunk['text'],
                'fund_name': metadata.get('fund_name', 'Unknown'),
                'chunk_type': metadata.get('chunk_type', 'general'),
                'similarity': similarity,
                'metadata': metadata  # Include full metadata for citation links
            })
        
        # Sort context by similarity
        context_parts.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Build context string
        context_text = "\n\n".join([
            f"[Source: {ctx['fund_name']} - {ctx['chunk_type']}]\n{ctx['text']}"
            for ctx in context_parts
        ])
        
        # Generate answer using Gemini with constraints
        answer = self._generate_answer(question, context_text)
        
        # Check if answer is an error message (rate limit, API errors, etc.)
        is_error_message = any(keyword in answer.lower() for keyword in [
            'error', 'encountered an error', 'experiencing high traffic', 
            'temporarily unavailable', 'rate limit', 'quota limit', 
            'api is currently', 'please wait a moment'
        ])
        
        if is_error_message:
            # For error messages, don't include citation_link or timestamp
            return {
                'answer': answer,
                'sources': [],
                'confidence': 0.0,
                'citation_link': '',  # No citation for errors
                'timestamp': None  # No timestamp for errors
            }
        
        # Format response with constraints for successful answers
        formatted = self.response_formatter.format_answer(
            answer,
            [
                {
                    'fund_name': ctx['fund_name'],
                    'chunk_type': ctx['chunk_type'],
                    'similarity': round(ctx['similarity'], 3)
                }
                for ctx in context_parts
            ],
            fund_name
        )
        
        return {
            'answer': formatted['answer'],
            'sources': formatted['sources'],
            'confidence': round(context_parts[0]['similarity'], 3) if context_parts else 0.0,
            'citation_link': formatted['citation_link'],
            'timestamp': formatted['timestamp']
        }
    
    def _generate_general_finance_answer(self, question: str) -> str:
        """
        Generate answer for general finance questions using LLM's general knowledge
        
        Args:
            question: User's question
            
        Returns:
            Generated answer
        """
        prompt = f"""You are a helpful and knowledgeable assistant for mutual funds and finance in India. Answer the following question about mutual funds or finance using your general knowledge.

CRITICAL CONSTRAINTS:
1. Provide factual, educational information only
2. DO NOT provide investment advice, recommendations, or opinions
3. DO NOT make performance claims or compute/compare returns
4. DO NOT refer to third-party blogs or external sources
5. Keep answer to maximum 3 sentences
6. Be clear, concise, and educational
7. Focus on explaining concepts, definitions, and general information
8. Always maintain a polite, friendly, and professional tone
9. If asked about specific funds, mention that you can provide details about HDFC funds if available

Question: {question}

Instructions:
- Answer the question based on general knowledge about mutual funds and finance
- Be factual, educational, and helpful
- Maximum 3 sentences
- Do not provide investment advice
- Always be courteous and helpful

Answer:"""
        
        try:
            # Use Gemini to generate answer
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            import urllib.request
            import json as json_lib
            
            json_data = json_lib.dumps(data).encode('utf-8')
            api_url = f"{self.gemini_client.api_url}?key={self.gemini_client.api_key}"
            
            req = urllib.request.Request(
                api_url,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json_lib.loads(response.read().decode('utf-8'))
            
            if 'candidates' in result and len(result['candidates']) > 0:
                answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
                return answer
            else:
                return "I couldn't generate an answer. Please try rephrasing your question."
                
        except Exception as e:
            logger.error(f"Error generating general finance answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using Gemini with retrieved context and constraints
        
        Args:
            question: User's question
            context: Retrieved context from chunks
            
        Returns:
            Generated answer
        """
        # Check if this is a greeting based on context
        is_greeting_context = "greeting" in context.lower() or "general conversation" in context.lower()
        
        if is_greeting_context:
            # Special prompt for greetings
            prompt = f"""You are a friendly and helpful assistant for mutual funds in India. A user has greeted you.

Respond politely and warmly to the greeting. Offer to help them with information about mutual funds.

Examples:
- "Hello" → "Hi! How can I help you with information about mutual funds today?"
- "Hi" → "Hello! I'm here to assist you with questions about mutual funds. What would you like to know?"
- "Thanks" → "You're welcome! Feel free to ask if you need any more information about mutual funds."
- "Good morning" → "Good morning! How can I assist you with mutual fund information today?"

Keep your response to 1-2 sentences, be warm and friendly.

User said: {question}

Your response:"""
        else:
            # Regular prompt for factual queries
            prompt = f"""You are a polite and helpful assistant for mutual funds in India. Your role is to provide factual information and assist users with a friendly, professional tone.

CRITICAL CONSTRAINTS:
1. Answer ONLY factual queries (expense ratios, exit loads, minimum SIP, lock-in periods, riskometer, benchmark, statement downloads)
2. DO NOT provide investment advice, recommendations, or opinions
3. DO NOT make performance claims or compute/compare returns
4. DO NOT refer to third-party blogs or external sources
5. Keep answer to maximum 3 sentences
6. Be precise with numbers and percentages - include ALL values mentioned in the context
7. If information is not in context, state that clearly
8. Always maintain a polite, friendly, and professional tone
9. When providing expense ratios, include BOTH Direct Plan and Regular Plan values if both are available in the context

Context (from official sources only):
{context}

Question: {question}

Instructions:
- Answer based ONLY on the provided context
- Be factual, precise, and polite
- Maximum 3 sentences
- Include ALL relevant numbers and percentages from the context (do not truncate)
- For expense ratios, mention both Direct Plan and Regular Plan if both are in the context
- Do not add performance claims or comparisons
- Do not provide investment advice
- Always be courteous and helpful

Answer:"""

        try:
            # Validate API key before making request
            if not self.gemini_client.api_key:
                raise ValueError("Gemini API key is not set")
            
            logger.debug(f"Making Gemini API request to: {self.gemini_client.api_url.split('?')[0]}")
            
            # Use the retry logic from GeminiClient
            result = self.gemini_client._make_api_request_with_retry(prompt)
            
            if 'candidates' in result and len(result['candidates']) > 0:
                answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
                return answer
            else:
                return "I couldn't generate an answer. Please try rephrasing your question."
                
        except urllib.error.HTTPError as e:
            # Handle rate limiting and other HTTP errors
            error_detail = str(e)
            try:
                error_body = e.read().decode('utf-8')
                import json as json_lib
                error_json = json_lib.loads(error_body)
                error_detail = error_json.get('error', {}).get('message', error_detail)
            except Exception:
                pass
            
            if e.code == 429:
                # Rate limit error - provide user-friendly message
                logger.error(f"Gemini API Rate Limit Error (429): {error_detail}")
                return "The API is currently experiencing high traffic. Please wait a moment and try again. If this persists, you may have reached your API quota limit."
            else:
                logger.error(f"Gemini API HTTP Error {e.code}: {error_detail}")
                # Don't expose technical details to users
                if "Resource exhausted" in error_detail or "429" in error_detail:
                    return "The service is temporarily unavailable due to high demand. Please try again in a few moments."
                return "I encountered an error while generating the answer. Please try again later."
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating answer: {e}", exc_info=True)
            # Check if it's a rate limit error in the message
            if "429" in error_msg or "rate limit" in error_msg.lower() or "Resource exhausted" in error_msg:
                return "The API is currently experiencing high traffic. Please wait a moment and try again."
            return "I encountered an error while generating the answer. Please try again later."
    
    def _extract_fund_name_from_query(self, query: str) -> Optional[str]:
        """
        Extract fund name from query using keyword matching
        
        Args:
            query: User query
            
        Returns:
            Extracted fund name or None
        """
        query_lower = query.lower()
        
        # Known fund patterns
        fund_patterns = [
            'hdfc large and mid cap fund',
            'hdfc flexi cap fund',
            'hdfc elss',
            'hdfc elss tax saver',
            'hdfc elss fund'
        ]
        
        for pattern in fund_patterns:
            if pattern in query_lower:
                # Map to actual fund names
                if 'elss' in pattern:
                    return 'HDFC ELSS Tax Saver Fund'
                elif 'large and mid cap' in pattern:
                    return 'HDFC Large and Mid Cap Fund'
                elif 'flexi cap' in pattern:
                    return 'HDFC Flexi Cap Fund'
        
        return None
    
    def _fuzzy_fund_match(self, query_fund: str, chunk_fund: str) -> bool:
        """
        Check if query fund name matches chunk fund name (fuzzy matching)
        
        Args:
            query_fund: Fund name from query
            chunk_fund: Fund name from chunk
            
        Returns:
            True if they match
        """
        query_lower = query_fund.lower()
        chunk_lower = chunk_fund.lower()
        
        # Extract key words (remove common words)
        query_words = set([w for w in query_lower.split() if w not in ['the', 'fund', 'mutual']])
        chunk_words = set([w for w in chunk_lower.split() if w not in ['the', 'fund', 'mutual']])
        
        # Check if most query words are in chunk words
        if len(query_words) == 0:
            return False
        
        match_ratio = len(query_words & chunk_words) / len(query_words)
        return match_ratio >= 0.6  # At least 60% of words match
    
    def _hybrid_search(self, query: str, query_embedding: List[float], 
                      chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic similarity with keyword matching
        
        Args:
            query: Original query text
            query_embedding: Query embedding vector
            chunks: Chunks to search
            top_k: Number of results to return
            
        Returns:
            List of similar chunks with boosted scores
        """
        query_lower = query.lower()
        
        # Extract key terms from query
        key_terms = []
        important_terms = ['expense ratio', 'exit load', 'minimum sip', 'lock-in', 
                          'riskometer', 'benchmark', 'nav', 'aum']
        for term in important_terms:
            if term in query_lower:
                key_terms.append(term)
        
        results = []
        
        for chunk in chunks:
            if 'embedding' not in chunk:
                chunk['embedding'] = self.embedding_store.generate_embedding(chunk['text'])
            
            # Semantic similarity
            semantic_sim = self.embedding_store.cosine_similarity(query_embedding, chunk['embedding'])
            
            # Keyword boost
            chunk_text_lower = chunk['text'].lower()
            keyword_boost = 0.0
            
            # Boost if key terms are found in chunk
            for term in key_terms:
                if term in chunk_text_lower:
                    keyword_boost += 0.3  # Significant boost for matching key terms
            
            # Boost if chunk type matches query intent
            chunk_type = chunk['metadata'].get('chunk_type', '')
            if 'expense' in query_lower or 'ratio' in query_lower:
                if chunk_type == 'fees_charges':
                    keyword_boost += 0.2
            elif 'exit load' in query_lower:
                if chunk_type == 'fees_charges':
                    keyword_boost += 0.2
            elif 'sip' in query_lower or 'minimum' in query_lower:
                if chunk_type == 'investment_details':
                    keyword_boost += 0.2
            elif 'lock' in query_lower:
                if chunk_type == 'investment_details':
                    keyword_boost += 0.2
            elif 'riskometer' in query_lower or 'benchmark' in query_lower:
                if chunk_type == 'risk_performance':
                    keyword_boost += 0.2
            
            # Combined score (semantic + keyword boost, capped at 1.0)
            combined_score = min(1.0, semantic_sim + keyword_boost)
            
            results.append({
                'chunk': chunk,
                'similarity': combined_score,
                'semantic_sim': semantic_sim,
                'keyword_boost': keyword_boost
            })
        
        # Sort by combined score
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def list_available_funds(self) -> List[str]:
        """
        List all funds available in the knowledge base
        
        Returns:
            List of fund names
        """
        funds = set()
        for chunk in self.chunks:
            fund_name = chunk['metadata'].get('fund_name', '')
            if fund_name:
                funds.add(fund_name)
        return sorted(list(funds))

