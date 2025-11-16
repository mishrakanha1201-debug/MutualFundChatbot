"""
Test script for API endpoints
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{API_BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_list_schemes():
    """Test schemes list endpoint"""
    print("Testing /api/schemes...")
    response = requests.get(f"{API_BASE_URL}/api/schemes")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_query_simple():
    """Test simple query endpoint"""
    print("Testing /api/query/simple...")
    question = "What is the expense ratio of HDFC Large and Mid Cap Fund?"
    response = requests.get(f"{API_BASE_URL}/api/query/simple", params={"question": question})
    print(f"Status: {response.status_code}")
    print(f"Question: {question}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_query_post():
    """Test POST query endpoint"""
    print("Testing POST /api/query...")
    
    queries = [
        {
            "question": "What is the minimum SIP amount for HDFC Flexi Cap Fund?",
            "fund_name": None
        },
        {
            "question": "What is the lock-in period for ELSS funds?",
            "fund_name": "HDFC ELSS Tax Saver Fund"
        }
    ]
    
    for query_data in queries:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json=query_data
        )
        print(f"Status: {response.status_code}")
        print(f"Question: {query_data['question']}")
        result = response.json()
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {len(result['sources'])} chunks")
        print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Test Suite")
    print("=" * 60)
    print()
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("Server is ready!\n")
                break
        except:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                print("Error: Server not responding. Make sure the API is running.")
                print("Start it with: python3 scripts/run_api.py")
                return
    
    # Run tests
    test_health()
    test_list_schemes()
    test_query_simple()
    test_query_post()
    
    print("=" * 60)
    print("Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()


