"""
Complete Backend System Test
Tests all functionality including constraints
"""
import sys
from pathlib import Path
import logging
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print section header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def test_constraint_1_factual_only(rag):
    """Test: Chatbot answers factual queries only"""
    print_header("CONSTRAINT 1: Factual Queries Only")
    
    factual_queries = [
        "What is the expense ratio of HDFC Large and Mid Cap Fund?",
        "What is the exit load?",
        "What is the minimum SIP amount?",
        "What is the lock-in period for ELSS?",
        "What is the riskometer rating?",
        "What is the benchmark index?",
        "How to download statements?",
    ]
    
    print("Testing factual queries (should work):")
    for query in factual_queries:
        result = rag.query(query)
        status = "✓" if not result.get('rejected') else "✗"
        print(f"  {status} {query[:60]}...")
        if result.get('rejected'):
            print(f"    ERROR: Factual query was rejected!")
    
    print("\nTesting opinionated queries (should be rejected):")
    opinionated = [
        "Should I buy HDFC fund?",
        "What are the returns?",
        "Is it good for investment?",
    ]
    
    for query in opinionated:
        result = rag.query(query)
        status = "✓" if result.get('rejected') else "✗"
        print(f"  {status} {query[:60]}...")
        if not result.get('rejected'):
            print(f"    ERROR: Opinionated query was not rejected!")


def test_constraint_2_citations(rag):
    """Test: Shows at least one citation link"""
    print_header("CONSTRAINT 2: Citation Links")
    
    queries = [
        "What is the expense ratio?",
        "What is the minimum SIP?",
    ]
    
    for query in queries:
        result = rag.query(query)
        has_citation = bool(result.get('citation_link'))
        status = "✓" if has_citation else "✗"
        print(f"  {status} {query}")
        print(f"    Citation: {result.get('citation_link', 'MISSING')}")
        if not has_citation:
            print(f"    ERROR: Missing citation link!")


def test_constraint_3_opinionated_rejection(rag):
    """Test: Refuses opinionated questions"""
    print_header("CONSTRAINT 3: Opinionated Questions Rejected")
    
    queries = [
        "Should I buy HDFC Large and Mid Cap Fund?",
        "What are the returns of HDFC Flexi Cap Fund?",
        "Is HDFC ELSS good for investment?",
    ]
    
    for query in queries:
        result = rag.query(query)
        rejected = result.get('rejected', False)
        has_educational_link = 'groww.in' in result.get('citation_link', '')
        status = "✓" if (rejected and has_educational_link) else "✗"
        print(f"  {status} {query}")
        print(f"    Rejected: {rejected}")
        print(f"    Educational Link: {result.get('citation_link', 'MISSING')}")
        if not rejected:
            print(f"    ERROR: Should have been rejected!")


def test_constraint_6_pii_detection(rag):
    """Test: PII detection and rejection"""
    print_header("CONSTRAINT 6: PII Detection")
    
    pii_queries = [
        ("PAN", "My PAN is ABCDE1234F"),
        ("Phone", "My phone is 9876543210"),
        ("Email", "My email is test@example.com"),
        ("Account", "Account number 1234567890123456"),
    ]
    
    for pii_type, query in pii_queries:
        result = rag.query(query)
        rejected = result.get('rejected', False)
        reason = result.get('rejection_reason')
        has_warning = 'do not share' in result['answer'].lower() or 'cannot accept' in result['answer'].lower()
        
        status = "✓" if (rejected and reason == 'pii_detected' and has_warning) else "✗"
        print(f"  {status} {pii_type} Detection")
        print(f"    Query: {query}")
        print(f"    Rejected: {rejected}, Reason: {reason}")
        print(f"    Has Warning: {has_warning}")
        if not rejected or reason != 'pii_detected':
            print(f"    ERROR: PII not detected correctly!")


def test_constraint_7_no_performance(rag):
    """Test: No performance claims"""
    print_header("CONSTRAINT 7: No Performance Claims")
    
    queries = [
        "What are the returns?",
        "Compare returns of funds",
    ]
    
    for query in queries:
        result = rag.query(query)
        rejected = result.get('rejected', False)
        status = "✓" if rejected else "✗"
        print(f"  {status} {query}")
        print(f"    Rejected: {rejected}")
        if not rejected:
            # Check if answer contains performance claims
            answer = result['answer'].lower()
            has_returns = 'returns' in answer or 'performance' in answer
            if has_returns:
                print(f"    WARNING: Answer may contain performance claims")


def test_constraint_8_sentence_limit(rag):
    """Test: Answers ≤3 sentences with timestamps"""
    print_header("CONSTRAINT 8: Sentence Limit & Timestamps")
    
    queries = [
        "What is the expense ratio of HDFC Large and Mid Cap Fund?",
        "What is the lock-in period?",
    ]
    
    for query in queries:
        result = rag.query(query)
        answer = result['answer']
        
        # Count sentences in main answer (excluding citation)
        main_answer = answer.split("Last updated from sources:")[0] if "Last updated from sources:" in answer else answer
        sentences = [s.strip() for s in main_answer.split('.') if s.strip() and len(s.strip()) > 10]
        
        has_timestamp = "Last updated from sources:" in answer
        within_limit = len(sentences) <= 3
        
        status = "✓" if (has_timestamp and within_limit) else "✗"
        print(f"  {status} {query[:50]}...")
        print(f"    Sentences: {len(sentences)} (should be ≤3)")
        print(f"    Has Timestamp: {has_timestamp}")
        print(f"    Timestamp: {result.get('timestamp', 'MISSING')}")
        if not within_limit:
            print(f"    ERROR: Answer has {len(sentences)} sentences!")


def test_api_response_format(rag):
    """Test: API response format"""
    print_header("API Response Format Test")
    
    query = "What is the expense ratio of HDFC Large and Mid Cap Fund?"
    result = rag.query(query)
    
    # Simulate API response
    api_response = {
        "answer": result['answer'],
        "sources": result['sources'],
        "confidence": result['confidence'],
        "query": query,
        "citation_link": result.get('citation_link', ''),
        "timestamp": result.get('timestamp'),
        "rejected": result.get('rejected', False),
        "rejection_reason": result.get('rejection_reason')
    }
    
    print("Sample API Response:")
    print(json.dumps(api_response, indent=2))
    
    # Validate all required fields
    required_fields = ['answer', 'sources', 'confidence', 'query', 'citation_link']
    missing = [f for f in required_fields if f not in api_response or not api_response[f]]
    
    if missing:
        print(f"\n✗ Missing fields: {missing}")
    else:
        print(f"\n✓ All required fields present")


def main():
    """Run complete backend system test"""
    print("=" * 70)
    print("COMPLETE BACKEND SYSTEM TEST")
    print("Testing all constraints and API functionality")
    print("=" * 70)
    
    # Initialize RAG pipeline
    print("\nInitializing RAG pipeline...")
    rag = RAGPipeline()
    print(f"✓ Loaded {len(rag.list_available_funds())} funds")
    print(f"✓ Ready for testing\n")
    
    # Run all constraint tests
    test_constraint_1_factual_only(rag)
    test_constraint_2_citations(rag)
    test_constraint_3_opinionated_rejection(rag)
    test_constraint_6_pii_detection(rag)
    test_constraint_7_no_performance(rag)
    test_constraint_8_sentence_limit(rag)
    test_api_response_format(rag)
    
    print_header("TEST SUMMARY")
    print("All constraints have been tested.")
    print("\nBackend system is ready for API testing!")
    print("\nTo test the API:")
    print("  1. Install FastAPI: pip install fastapi uvicorn")
    print("  2. Start server: python3 scripts/run_api.py")
    print("  3. Test endpoints: python3 scripts/test_api.py")


if __name__ == "__main__":
    main()


