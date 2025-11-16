"""
Test script for RAG Pipeline
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test RAG pipeline with sample queries"""
    print("=" * 60)
    print("RAG Pipeline Test")
    print("=" * 60)
    
    # Initialize RAG pipeline
    print("\nInitializing RAG pipeline...")
    rag = RAGPipeline()
    
    # List available funds
    print(f"\nAvailable funds: {', '.join(rag.list_available_funds())}")
    
    # Test queries
    test_queries = [
        "What is the expense ratio of HDFC Large and Mid Cap Fund?",
        "What is the minimum SIP amount for HDFC Flexi Cap Fund?",
        "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
        "What is the exit load for HDFC Large and Mid Cap Fund?",
        "What is the benchmark index for HDFC Flexi Cap Fund?",
    ]
    
    print("\n" + "=" * 60)
    print("Testing Queries")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 60)
        
        result = rag.query(query)
        
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {len(result['sources'])} chunks")
        for source in result['sources']:
            print(f"  - {source['fund_name']} ({source['chunk_type']}) - similarity: {source['similarity']}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()


