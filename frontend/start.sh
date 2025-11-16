#!/bin/bash
# Simple script to start the frontend server

cd "$(dirname "$0")"
echo "Starting frontend server on http://localhost:3000"
echo "Press Ctrl+C to stop"
python3 serve.py


