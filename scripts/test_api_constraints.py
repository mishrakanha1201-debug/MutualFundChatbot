"""
Test API with constraints - Simulates API calls
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def simulate_api_call(rag, query, fund_name=None):
    """Simulate API call"""
    result = rag.query(query, fund_name=fund_name)
    
    response = {
        "answer": result['answer'],
        "sources": [
            {
                "fund_name": s['fund_name'],
                "chunk_type": s['chunk_type'],
                "similarity": s['similarity']
            }
            for s in result['sources']
        ],
        "confidence": result['confidence'],
        "query": query,
        "citation_link": result.get('citation_link', ''),
        "timestamp": result.get('timestamp'),
        "rejected": result.get('rejected', False),
        "rejection_reason": result.get('rejection_reason')
    }
    
    return response


def main():
    """Test API responses with constraints"""
    print("=" * 70)
    print("API CONSTRAINT TESTING")
    print("=" * 70)
    
    rag = RAGPipeline()
    
    test_cases = [
        {
            "name": "Factual Query - Expense Ratio",
            "query": "What is the expense ratio of HDFC Large and Mid Cap Fund?",
            "expected_rejected": False,
            "should_have_citation": True
        },
        {
            "name": "Opinionated Query - Investment Advice",
            "query": "Should I buy HDFC Flexi Cap Fund?",
            "expected_rejected": True,
            "expected_reason": "opinionated"
        },
        {
            "name": "PII Detection - PAN",
            "query": "My PAN is ABCDE1234F",
            "expected_rejected": True,
            "expected_reason": "pii_detected"
        },
        {
            "name": "Factual Query - Lock-in Period",
            "query": "What is the lock-in period for ELSS funds?",
            "expected_rejected": False,
            "should_have_citation": True
        },
        {
            "name": "Performance Query - Should Reject",
            "query": "What are the returns of HDFC funds?",
            "expected_rejected": True,
            "expected_reason": "opinionated"
        }
    ]
    
    print("\nRunning test cases...\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Query: {test['query']}")
        
        response = simulate_api_call(rag, test['query'])
        
        # Validate constraints
        checks = []
        
        # Check rejection
        if test.get('expected_rejected'):
            if response['rejected']:
                checks.append("✓ Correctly rejected")
                if test.get('expected_reason'):
                    if response['rejection_reason'] == test['expected_reason']:
                        checks.append(f"✓ Correct reason: {test['expected_reason']}")
                    else:
                        checks.append(f"✗ Wrong reason: {response['rejection_reason']} (expected {test['expected_reason']})")
                        failed += 1
                        continue
            else:
                checks.append("✗ Should have been rejected but wasn't")
                failed += 1
                print(f"  {' | '.join(checks)}\n")
                continue
        else:
            if not response['rejected']:
                checks.append("✓ Not rejected (correct)")
            else:
                checks.append(f"✗ Incorrectly rejected: {response['rejection_reason']}")
                failed += 1
                print(f"  {' | '.join(checks)}\n")
                continue
        
        # Check citation
        if test.get('should_have_citation'):
            if response['citation_link']:
                checks.append("✓ Has citation link")
            else:
                checks.append("✗ Missing citation link")
                failed += 1
        
        # Check timestamp
        if response.get('timestamp'):
            checks.append("✓ Has timestamp")
        else:
            checks.append("✗ Missing timestamp")
        
        # Check answer length (main answer, not citation)
        answer = response['answer']
        main_answer = answer.split("Last updated from sources:")[0] if "Last updated from sources:" in answer else answer
        sentences = [s.strip() for s in main_answer.split('.') if s.strip() and len(s.strip()) > 10]
        if len(sentences) <= 3:
            checks.append("✓ Answer ≤3 sentences")
        else:
            checks.append(f"✗ Answer too long: {len(sentences)} sentences")
            failed += 1
        
        print(f"  {' | '.join(checks)}")
        print(f"  Answer preview: {response['answer'][:100]}...")
        print()
        
        if all("✓" in c for c in checks):
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


