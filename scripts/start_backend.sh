#!/bin/bash
# Script to start the backend API server

cd "$(dirname "$0")/.."
echo "Starting Backend API on http://localhost:8000"
echo "Press Ctrl+C to stop"
python3 scripts/run_api.py


