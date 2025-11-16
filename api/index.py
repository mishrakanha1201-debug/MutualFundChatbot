"""
Vercel serverless function entrypoint for FastAPI
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH for imports
os.environ['PYTHONPATH'] = str(project_root)

# Import FastAPI app
from backend.api.main import app

# Export the app for Vercel
__all__ = ['app']

