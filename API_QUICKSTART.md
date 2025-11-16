# API Quick Start Guide

## Installation

```bash
pip install fastapi uvicorn
```

## Start the Server

```bash
python3 scripts/run_api.py
```

The API will start at: `http://localhost:8000`

## Quick Test

### Using curl:

```bash
# Health check
curl http://localhost:8000/api/health

# List funds
curl http://localhost:8000/api/schemes

# Ask a question (GET)
curl "http://localhost:8000/api/query/simple?question=What is the expense ratio?"

# Ask a question (POST)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the minimum SIP amount?"}'
```

### Using Python:

```python
import requests

# Query
response = requests.post(
    "http://localhost:8000/api/query",
    json={"question": "What is the expense ratio of HDFC Large and Mid Cap Fund?"}
)

print(response.json()["answer"])
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI


