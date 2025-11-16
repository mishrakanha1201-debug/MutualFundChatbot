"""
Simple HTTP server for the API (no FastAPI required)
Uses Python standard library only
"""
import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize RAG pipeline
logger.info("Initializing RAG pipeline...")
rag_pipeline = RAGPipeline()
logger.info("RAG pipeline ready!")


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API endpoints"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/health':
            self.handle_health()
        elif path == '/api/schemes':
            self.handle_schemes()
        elif path == '/api/query/simple':
            self.handle_simple_query(parsed_path.query)
        elif path == '/':
            # Root endpoint
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"message":"Mutual Fund FAQ Bot API"}')
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/query':
            self.handle_query()
        else:
            self.send_error(404, "Not Found")
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
    
    def handle_health(self):
        """Handle health check endpoint"""
        try:
            # Get fund count from chunks metadata
            fund_names = set()
            for chunk in rag_pipeline.chunks:
                fund_name = chunk.get('metadata', {}).get('fund_name', '')
                if fund_name:
                    fund_names.add(fund_name)
            
            response = {
                "status": "ok",
                "message": "API is running smoothly.",
                "rag_initialized": True,
                "total_funds_indexed": len(fund_names),
                "total_chunks_indexed": len(rag_pipeline.chunks)
            }
            response_json = json.dumps(response)
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(response_json.encode('utf-8'))
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.send_error(500, str(e))
    
    def handle_schemes(self):
        """Handle schemes list endpoint"""
        try:
            # Extract fund information from chunks
            funds_map = {}
            for chunk in rag_pipeline.chunks:
                metadata = chunk.get('metadata', {})
                fund_name = metadata.get('fund_name', '')
                if fund_name and fund_name not in funds_map:
                    funds_map[fund_name] = {
                        "fund_name": fund_name,
                        "fund_category": metadata.get('fund_category'),
                        "aum": metadata.get('aum'),
                        "riskometer": metadata.get('riskometer')
                    }
            
            funds_details = list(funds_map.values())
            
            response = {"funds": funds_details}
            response_json = json.dumps(response)
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(response_json.encode('utf-8'))
        except Exception as e:
            logger.error(f"Schemes error: {e}")
            self.send_error(500, str(e))
    
    def handle_query(self):
        """Handle query POST request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if not post_data:
                self.send_error(400, "No data provided")
                return
            
            data = json.loads(post_data.decode('utf-8'))
            question = data.get('question', '')
            
            if not question:
                self.send_error(400, "Question is required")
                return
            
            # Process query
            result = rag_pipeline.query(question)
            
            # Format response
            response = {
                "answer": result['answer'],
                "sources": [
                    {
                        "fund_name": src['fund_name'],
                        "chunk_type": src['chunk_type'],
                        "similarity": src['similarity']
                    }
                    for src in result['sources']
                ],
                "confidence": result['confidence'],
                "query": question,
                "citation_link": result.get('citation_link', ''),
                "timestamp": result.get('timestamp'),
                "rejected": result.get('rejected', False),
                "rejection_reason": result.get('rejection_reason')
            }
            
            response_json = json.dumps(response)
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(response_json.encode('utf-8'))
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_simple_query(self, query_string):
        """Handle simple GET query"""
        try:
            params = parse_qs(query_string)
            question = params.get('question', [''])[0]
            
            if not question:
                self.send_error(400, "Question parameter is required")
                return
            
            # Process query
            result = rag_pipeline.query(question)
            
            # Format response
            response = {
                "answer": result['answer'],
                "sources": [
                    {
                        "fund_name": src['fund_name'],
                        "chunk_type": src['chunk_type'],
                        "similarity": src['similarity']
                    }
                    for src in result['sources']
                ],
                "confidence": result['confidence'],
                "query": question,
                "citation_link": result.get('citation_link', ''),
                "timestamp": result.get('timestamp'),
                "rejected": result.get('rejected', False),
                "rejection_reason": result.get('rejection_reason')
            }
            
            response_json = json.dumps(response)
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Simple query error: {e}")
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Start the HTTP server"""
    import os
    # Use PORT environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    logger.info(f"Starting API server on port {port}")
    logger.info("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nServer stopped")
        httpd.server_close()


if __name__ == "__main__":
    main()

