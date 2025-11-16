# Mutual Fund FAQ Bot - API Documentation

## Phase 3: Backend API Development

### Installation

Install required dependencies:
```bash
pip install fastapi uvicorn
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### Running the API

Start the API server:
```bash
python3 scripts/run_api.py
```

The API will be available at: `http://localhost:8000`

### API Endpoints

#### 1. Root Endpoint
- **URL**: `GET /`
- **Description**: API information and available endpoints
- **Response**: JSON with API details

#### 2. Health Check
- **URL**: `GET /api/health`
- **Description**: Check API health and RAG pipeline status
- **Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "rag_initialized": true,
  "chunks_loaded": 30,
  "funds_available": 3
}
```

#### 3. List Available Schemes
- **URL**: `GET /api/schemes`
- **Description**: Get list of all available mutual fund schemes
- **Response**:
```json
{
  "funds": [
    {"name": "HDFC Large and Mid Cap Fund", "available": true},
    {"name": "HDFC Flexi Cap Fund", "available": true},
    {"name": "HDFC ELSS Tax Saver Fund", "available": true}
  ],
  "total": 3
}
```

#### 4. Query (POST)
- **URL**: `POST /api/query`
- **Description**: Ask questions about mutual funds
- **Request Body**:
```json
{
  "question": "What is the expense ratio of HDFC Large and Mid Cap Fund?",
  "fund_name": "HDFC Large and Mid Cap Fund",  // Optional
  "top_k": 3  // Optional, default: 3
}
```
- **Response**:
```json
{
  "answer": "The expense ratio for HDFC Large and Mid Cap Fund...",
  "sources": [
    {
      "fund_name": "HDFC Large and Mid Cap Fund",
      "chunk_type": "fees_charges",
      "similarity": 0.471
    }
  ],
  "confidence": 0.471,
  "query": "What is the expense ratio of HDFC Large and Mid Cap Fund?"
}
```

#### 5. Query (Simple GET)
- **URL**: `GET /api/query/simple?question=YOUR_QUESTION`
- **Description**: Simple GET endpoint for easy testing
- **Example**: `GET /api/query/simple?question=What is the minimum SIP amount?`
- **Response**: Simplified JSON with answer and confidence

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing

Run the test suite:
```bash
# In one terminal, start the API:
python3 scripts/run_api.py

# In another terminal, run tests:
python3 scripts/test_api.py
```

### Example Usage

#### Using curl:
```bash
# Health check
curl http://localhost:8000/api/health

# List schemes
curl http://localhost:8000/api/schemes

# Query (GET)
curl "http://localhost:8000/api/query/simple?question=What is the expense ratio?"

# Query (POST)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the minimum SIP amount for HDFC Flexi Cap Fund?"}'
```

#### Using Python:
```python
import requests

# Query
response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "question": "What is the expense ratio of HDFC Large and Mid Cap Fund?",
        "fund_name": "HDFC Large and Mid Cap Fund"
    }
)

result = response.json()
print(result["answer"])
```

### Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error
- `503`: Service Unavailable (RAG pipeline not initialized)

Error responses follow this format:
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```


