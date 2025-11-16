"""
Interactive Chatbot for Mutual Fund FAQ
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce verbosity for interactive use
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run interactive chatbot"""
    print("=" * 60)
    print("Mutual Fund FAQ Chatbot")
    print("=" * 60)
    print("\nInitializing...")
    
    # Initialize RAG pipeline
    rag = RAGPipeline()
    
    print(f"✓ Loaded {len(rag.list_available_funds())} funds")
    print(f"✓ Ready to answer questions!\n")
    print("Available funds:")
    for fund in rag.list_available_funds():
        print(f"  - {fund}")
    print("\nType 'quit' or 'exit' to end the conversation")
    print("=" * 60)
    print()
    
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                continue
            
            print("\nThinking...")
            result = rag.query(question)
            
            print(f"\nBot: {result['answer']}")
            
            if result['sources']:
                print(f"\n[Sources: {len(result['sources'])} relevant chunks found]")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()


