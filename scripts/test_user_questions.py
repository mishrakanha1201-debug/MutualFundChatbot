"""
Test backend with user-provided test questions
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


def test_questions():
    """Test with user-provided questions"""
    print("=" * 70)
    print("BACKEND TEST - User Questions")
    print("=" * 70)
    
    # Initialize RAG pipeline
    print("\nInitializing RAG pipeline...")
    rag = RAGPipeline()
    print(f"✓ Ready with {len(rag.list_available_funds())} funds\n")
    
    # Test questions
    test_questions = [
        "Give a description of HDFC Large and Mid Cap Mutual Fund",
        "What is the meaning of Flexi Cap?",
        "Expense ratio of HDFC ELSS Fund?",
        "What is HDFC ELSS Fund lock-in period?",
        "What is the minimum SIP amount for HDFC Flexi Cap Fund?",
        "What is the exit load of HDFC Large and Mid Cap Mutual Fund?",
        "Give an overview of the Riskometer/benchmark of HDFC ELSS fund?",
        "How to download capital-gains statements?",
    ]
    
    print("=" * 70)
    print("Testing Questions")
    print("=" * 70)
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 70)
        
        result = rag.query(question)
        results.append({
            'question': question,
            'result': result
        })
        
        # Display results
        if result.get('rejected'):
            print(f"   Status: REJECTED")
            print(f"   Reason: {result.get('rejection_reason', 'unknown')}")
            print(f"   Message: {result['answer']}")
        else:
            print(f"   Status: ANSWERED")
            print(f"   Answer: {result['answer']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Sources: {len(result['sources'])} chunks")
            if result.get('citation_link'):
                print(f"   Citation: {result['citation_link']}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    answered = sum(1 for r in results if not r['result'].get('rejected'))
    rejected = sum(1 for r in results if r['result'].get('rejected'))
    
    print(f"\nTotal Questions: {len(test_questions)}")
    print(f"Answered: {answered}")
    print(f"Rejected: {rejected}")
    
    print("\nDetailed Results:")
    for i, item in enumerate(results, 1):
        status = "REJECTED" if item['result'].get('rejected') else "ANSWERED"
        print(f"  {i}. {status}: {item['question'][:60]}...")
    
    return results


if __name__ == "__main__":
    test_questions()


