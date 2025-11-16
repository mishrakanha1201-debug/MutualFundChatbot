"""
Run the FastAPI server
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uvicorn
except ImportError:
    print("Error: uvicorn not installed")
    print("Please install: pip install uvicorn")
    sys.exit(1)

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )


