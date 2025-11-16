"""
Test script for chatbot constraints
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline
from backend.rag.query_classifier import QueryClassifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def test_query_classifier():
    """Test query classification"""
    print("=" * 60)
    print("Testing Query Classifier")
    print("=" * 60)
    
    classifier = QueryClassifier()
    
    test_queries = [
        ("What is the expense ratio of HDFC Large and Mid Cap Fund?", "factual"),
        ("Should I buy HDFC Flexi Cap Fund?", "opinionated"),
        ("What is the minimum SIP amount?", "factual"),
        ("Compare returns of HDFC funds", "opinionated"),
        ("My PAN is ABCDE1234F", "pii"),
        ("My phone number is 9876543210", "pii"),
        ("What is the lock-in period for ELSS?", "factual"),
        ("Is HDFC fund good for investment?", "opinionated"),
    ]
    
    for query, expected_type in test_queries:
        result = classifier.classify_query(query)
        print(f"\nQuery: {query}")
        print(f"  Expected: {expected_type}")
        print(f"  Is Factual: {result['is_factual']}")
        print(f"  Is Opinionated: {result['is_opinionated']}")
        print(f"  PII Detected: {result['pii_detected']}")
        print(f"  Can Answer: {result['can_answer']}")
        if not result['can_answer']:
            print(f"  Rejection Reason: {result['rejection_reason']}")


def test_rag_with_constraints():
    """Test RAG pipeline with constraints"""
    print("\n" + "=" * 60)
    print("Testing RAG Pipeline with Constraints")
    print("=" * 60)
    
    rag = RAGPipeline()
    
    test_queries = [
        # Factual queries (should work)
        ("What is the expense ratio of HDFC Large and Mid Cap Fund?", True),
        ("What is the minimum SIP amount for HDFC Flexi Cap Fund?", True),
        ("What is the lock-in period for HDFC ELSS Tax Saver Fund?", True),
        
        # Opinionated queries (should be rejected)
        ("Should I buy HDFC Large and Mid Cap Fund?", False),
        ("What are the returns of HDFC Flexi Cap Fund?", False),
        ("Is HDFC ELSS good for investment?", False),
        
        # PII queries (should be rejected)
        ("My PAN is ABCDE1234F, what is the expense ratio?", False),
    ]
    
    for query, should_work in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Expected: {'Should work' if should_work else 'Should be rejected'}")
        print("-" * 60)
        
        result = rag.query(query)
        
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Rejected: {result.get('rejected', False)}")
        if result.get('citation_link'):
            print(f"Citation: {result['citation_link']}")
        if result.get('rejection_reason'):
            print(f"Rejection Reason: {result['rejection_reason']}")


def main():
    """Run all constraint tests"""
    test_query_classifier()
    test_rag_with_constraints()
    
    print("\n" + "=" * 60)
    print("Constraint Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()


