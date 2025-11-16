"""
Test greeting functionality
"""
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def test_greetings():
    """Test greeting responses"""
    print("=" * 70)
    print("Testing Greeting Functionality")
    print("=" * 70)
    
    rag = RAGPipeline()
    
    greetings = [
        "Hello",
        "Hi",
        "Hey",
        "Good morning",
        "Thanks",
        "Thank you",
        "Bye",
    ]
    
    print("\nTesting greetings:")
    for greeting in greetings:
        print(f"\nUser: {greeting}")
        result = rag.query(greeting)
        print(f"Bot: {result['answer']}")
        print(f"Rejected: {result.get('rejected', False)}")
    
    print("\n" + "=" * 70)
    print("Greeting tests complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_greetings()


