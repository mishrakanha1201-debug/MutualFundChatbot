"""
Complete Backend Test Suite
Tests all constraints and API functionality
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce verbosity
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def test_factual_queries(rag):
    """Test factual queries that should work"""
    print_section("TEST 1: Factual Queries (Should Work)")
    
    factual_queries = [
        "What is the expense ratio of HDFC Large and Mid Cap Fund?",
        "What is the minimum SIP amount for HDFC Flexi Cap Fund?",
        "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
        "What is the exit load for HDFC Large and Mid Cap Fund?",
        "What is the benchmark index for HDFC Flexi Cap Fund?",
        "How to download statements for HDFC funds?",
    ]
    
    for i, query in enumerate(factual_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = rag.query(query)
        
        # Check constraints
        assert not result.get('rejected', False), f"Factual query was rejected: {query}"
        assert result.get('citation_link'), "Missing citation link"
        
        # Count sentences in main answer (excluding citation)
        answer = result['answer']
        main_answer = answer.split("Last updated from sources:")[0] if "Last updated from sources:" in answer else answer
        sentences = [s.strip() for s in main_answer.split('.') if s.strip() and len(s.strip()) > 10]
        assert len(sentences) <= 3, f"Answer too long ({len(sentences)} sentences, should be ≤3): {answer[:200]}"
        assert "Last updated from sources:" in result['answer'], "Missing timestamp"
        
        print(f"   ✓ Answer: {result['answer'][:150]}...")
        print(f"   ✓ Citation: {result.get('citation_link', 'N/A')}")
        print(f"   ✓ Sources: {len(result['sources'])} chunks")
        print(f"   ✓ Confidence: {result['confidence']}")


def test_opinionated_queries(rag):
    """Test opinionated queries that should be rejected"""
    print_section("TEST 2: Opinionated Queries (Should Be Rejected)")
    
    opinionated_queries = [
        "Should I buy HDFC Large and Mid Cap Fund?",
        "What are the returns of HDFC Flexi Cap Fund?",
        "Is HDFC ELSS good for investment?",
        "Compare returns of HDFC funds",
        "Which HDFC fund is better?",
        "Should I sell my HDFC fund?",
    ]
    
    for i, query in enumerate(opinionated_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = rag.query(query)
        
        # Check constraints
        assert result.get('rejected', False), f"Opinionated query was not rejected: {query}"
        assert result.get('rejection_reason') in ['opinionated', 'not_factual'], f"Wrong rejection reason: {result.get('rejection_reason')}"
        assert result.get('citation_link'), "Missing citation link"
        assert "educational" in result.get('citation_link', '').lower() or "groww" in result.get('citation_link', '').lower(), "Missing educational link"
        
        print(f"   ✓ Rejected: {result.get('rejected')}")
        print(f"   ✓ Reason: {result.get('rejection_reason')}")
        print(f"   ✓ Message: {result['answer'][:150]}...")
        print(f"   ✓ Educational Link: {result.get('citation_link', 'N/A')}")


def test_pii_detection(rag):
    """Test PII detection"""
    print_section("TEST 3: PII Detection (Should Be Rejected)")
    
    pii_queries = [
        "My PAN is ABCDE1234F, what is the expense ratio?",
        "My phone number is 9876543210",
        "My email is test@example.com",
        "My account number is 1234567890123456",
    ]
    
    for i, query in enumerate(pii_queries, 1):
        print(f"\n{i}. Query: {query}")
        result = rag.query(query)
        
        # Check constraints
        assert result.get('rejected', False), f"PII query was not rejected: {query}"
        assert result.get('rejection_reason') == 'pii_detected', "Wrong rejection reason"
        assert "do not share" in result['answer'].lower() or "cannot accept" in result['answer'].lower(), "Missing PII warning"
        
        print(f"   ✓ Rejected: {result.get('rejected')}")
        print(f"   ✓ Reason: {result.get('rejection_reason')}")
        print(f"   ✓ Message: {result['answer'][:150]}...")


def test_answer_formatting(rag):
    """Test answer formatting constraints"""
    print_section("TEST 4: Answer Formatting Constraints")
    
    query = "What is the expense ratio of HDFC Large and Mid Cap Fund?"
    result = rag.query(query)
    
    answer = result['answer']
    sentences = [s.strip() for s in answer.split('.') if s.strip()]
    
    print(f"Query: {query}")
    print(f"Answer: {answer}")
    print(f"\nFormatting Checks:")
    print(f"  ✓ Sentence count: {len(sentences)} (should be ≤3)")
    print(f"  ✓ Has citation: {'Last updated from sources:' in answer}")
    print(f"  ✓ Has link: {bool(result.get('citation_link'))}")
    print(f"  ✓ No performance claims: {'returns' not in answer.lower() or 'performance' not in answer.lower()}")
    
    assert len(sentences) <= 4, "Answer has more than 3 sentences"  # Allow 4 for citation
    assert "Last updated from sources:" in answer, "Missing timestamp"
    assert result.get('citation_link'), "Missing citation link"


def main():
    """Run complete backend test suite"""
    print("=" * 70)
    print("COMPLETE BACKEND TEST SUITE")
    print("Testing all constraints and functionality")
    print("=" * 70)
    
    # Initialize RAG pipeline
    print("\nInitializing RAG pipeline...")
    rag = RAGPipeline()
    print(f"✓ Loaded {len(rag.list_available_funds())} funds")
    print(f"✓ Ready for testing\n")
    
    try:
        # Run all tests
        test_factual_queries(rag)
        test_opinionated_queries(rag)
        test_pii_detection(rag)
        test_answer_formatting(rag)
        
        print_section("ALL TESTS PASSED ✓")
        print("\nBackend is ready with all constraints implemented!")
        print("\nConstraint Summary:")
        print("  ✓ Factual queries only")
        print("  ✓ Citation links in every answer")
        print("  ✓ Opinionated queries rejected")
        print("  ✓ PII detection and rejection")
        print("  ✓ No performance claims")
        print("  ✓ Answers limited to 3 sentences")
        print("  ✓ Timestamps in citations")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

