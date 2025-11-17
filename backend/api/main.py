"""
FastAPI Backend for Mutual Fund FAQ Bot
"""
import sys
from pathlib import Path
from typing import Optional
import logging
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    # Fallback if FastAPI not installed
    print("FastAPI not installed. Please install: pip install fastapi uvicorn")
    sys.exit(1)

from backend.api.models import (
    QueryRequest, QueryResponse, FundsResponse, 
    HealthResponse, ErrorResponse, SourceInfo
)
from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund FAQ Bot API",
    description="API for querying mutual fund information using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline instance
rag_pipeline: Optional[RAGPipeline] = None
rag_init_error: Optional[str] = None  # Store initialization error for better error messages


# Initialize RAG pipeline (lazy initialization for serverless)
def get_rag_pipeline():
    """Get or initialize RAG pipeline (lazy loading for serverless)"""
    global rag_pipeline, rag_init_error
    if rag_pipeline is None:
        try:
            logger.info("Initializing RAG pipeline...")
            # Check for required environment variables
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                error_msg = "GEMINI_API_KEY environment variable not set. Please configure it in Vercel project settings under Environment Variables."
                logger.error(error_msg)
                rag_init_error = error_msg
                raise ValueError(error_msg)
            
            # Determine data directory path (works in both local and Vercel)
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data" / "scraped"
            embeddings_dir = project_root / "data" / "embeddings"
            
            # Log paths for debugging
            logger.info(f"Project root: {project_root}")
            logger.info(f"Data directory: {data_dir} (exists: {data_dir.exists()})")
            logger.info(f"Embeddings directory: {embeddings_dir} (exists: {embeddings_dir.exists()})")
            
            # Check if data directory exists
            if not data_dir.exists():
                logger.warning(f"Data directory not found at {data_dir}, trying alternative paths...")
                # Try alternative paths
                alt_paths = [
                    Path.cwd() / "data" / "scraped",
                    Path("/var/task/data/scraped"),  # Vercel serverless
                    Path("/tmp/data/scraped"),  # Alternative serverless
                ]
                for alt_path in alt_paths:
                    if alt_path.exists():
                        data_dir = alt_path
                        embeddings_dir = alt_path.parent / "embeddings"
                        logger.info(f"Using alternative data directory: {data_dir}")
                        break
                else:
                    error_msg = f"Data directory not found. Tried: {data_dir} and alternatives. Please ensure data files are included in deployment."
                    logger.error(error_msg)
                    rag_init_error = error_msg
                    raise FileNotFoundError(error_msg)
            
            rag_pipeline = RAGPipeline(
                data_dir=str(data_dir),
                embeddings_dir=str(embeddings_dir)
            )
            logger.info(f"RAG pipeline initialized successfully with {len(rag_pipeline.chunks)} chunks")
            rag_init_error = None  # Clear error on success
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error initializing RAG pipeline: {e}", exc_info=True)
            # Store more specific error message
            if "GEMINI_API_KEY" in error_msg or "Gemini API key" in error_msg:
                rag_init_error = "Gemini API key is missing or invalid. Please set GEMINI_API_KEY in Vercel environment variables."
            elif "Data directory" in error_msg or "not found" in error_msg:
                rag_init_error = "Data files not found. Please ensure scraped data is included in the deployment."
            else:
                rag_init_error = f"Failed to initialize RAG pipeline: {error_msg}"
            rag_pipeline = None
    return rag_pipeline

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup (for traditional deployments)"""
    get_rag_pipeline()

# Load frontend files for Vercel serverless deployment
# Try to load from public directory (works in local dev), fall back to reading at runtime
try:
    project_root = Path(__file__).parent.parent.parent
    public_path = project_root / "public"
    logger.info(f"Project root: {project_root}, Public path: {public_path}, Exists: {public_path.exists()}")
except Exception as e:
    logger.error(f"Error setting up paths: {e}")
    project_root = Path.cwd()
    public_path = project_root / "public"

def load_frontend_file(filename: str) -> str:
    """Load frontend file from public directory - tries multiple paths for Vercel"""
    # Try multiple possible paths
    possible_paths = [
        public_path / filename,  # Standard path
        project_root / "public" / filename,  # Explicit project root
        Path.cwd() / "public" / filename,  # Current working directory
        Path(__file__).parent.parent.parent / "public" / filename,  # From this file
    ]
    
    for file_path in possible_paths:
        abs_path = file_path.resolve() if file_path.exists() else file_path
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content:
                        logger.info(f"Successfully loaded {filename} from {abs_path} ({len(content)} chars)")
                        return content
                    else:
                        logger.warning(f"File {filename} at {abs_path} is empty")
            except Exception as e:
                logger.warning(f"Error reading {filename} from {abs_path}: {e}")
                continue
    
    logger.error(f"Could not load {filename} from any path. Tried: {[str(p.resolve() if p.exists() else p) for p in possible_paths]}")
    return ""

# Generate HTML with embedded frontend files
def generate_frontend_html(app_jsx_content: str, styles_css_content: str) -> str:
    """Generate HTML with embedded JSX and CSS"""
    # Escape for HTML/JavaScript - need to escape script tags and handle special chars
    def escape_for_html(s):
        # Escape script closing tags to prevent breaking out of script tag
        s = s.replace('</script>', '<\\/script>')
        # Escape backslashes
        s = s.replace('\\', '\\\\')
        return s
    
    app_jsx_escaped = escape_for_html(app_jsx_content)
    styles_css_escaped = escape_for_html(styles_css_content)
    
    # Use string concatenation instead of .format() to avoid conflicts with CSS/JSX curly braces
    html_parts = [
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mutual Fund Broww - Groww</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #FFFFFF;
            color: #44475B;
            line-height: 1.5;
        }
        
        #root {
            width: 100%;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
    </style>
    <style id="app-styles">""",
        styles_css_escaped,
        """</style>
</head>
<body>
    <div id="root"></div>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
""",
        app_jsx_escaped,
        """
    </script>
</body>
</html>"""
    ]
    
    return ''.join(html_parts)

# Embedded frontend files (always available, no file system dependency)
# These are embedded directly to work in Vercel serverless environment
FRONTEND_APP_JSX = """const { useState, useEffect, useRef } = React;

// API Configuration
// Use relative URL for same-domain deployment (Vercel), fallback to localhost for development
const API_BASE_URL = window.location.origin || 'http://localhost:8000';

// Welcome State Component
function WelcomeState({ onQuestionClick }) {
    const exampleQuestions = [
        "What is the exit load for HDFC Flexi Cap Fund?",
        "What is HDFC ELSS fund lock-in period?",
        "Expense ratio of HDFC Large and Mid Cap Fund?"
    ];

    return (
        <div className="welcome-state">
            <p className="welcome-message">
                Hi! I can help you find quick facts about mutual fund schemes from official sources.
            </p>
            <p className="welcome-disclaimer">
                Facts-only. No investment advice.
            </p>
            <div className="example-questions">
                {exampleQuestions.map((question, index) => (
                    <button
                        key={index}
                        className="example-question-chip"
                        onClick={() => onQuestionClick(question)}
                    >
                        {question}
                    </button>
                ))}
            </div>
        </div>
    );
}

// Message Bubble Component
function MessageBubble({ message, isUser, source, timestamp }) {
    if (isUser) {
        return (
            <div className="message-bubble user-bubble">
                {message}
            </div>
        );
    }

    // Parse assistant message to extract answer text (remove citation if present)
    let answerText = message;
    if (answerText.includes('Last updated from sources:')) {
        answerText = answerText.split('Last updated from sources:')[0].trim();
    }
    if (answerText.includes('For more details, visit:')) {
        answerText = answerText.split('For more details, visit:')[0].trim();
    }

    return (
        <div className="message-bubble assistant-bubble">
            <div className="answer-text">{answerText}</div>
            {source && (
                <a 
                    href={source} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="source-link"
                >
                    View Source →
                </a>
            )}
            {timestamp && (
                <div className="timestamp">
                    Last updated from sources: {timestamp}
                </div>
            )}
        </div>
    );
}

// Loading Bubble Component
function LoadingBubble() {
    return (
        <div className="message-bubble loading-bubble">
            <div className="loading-dots">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
            </div>
        </div>
    );
}

// Main Chat Component
function ChatApp() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleQuestionClick = (question) => {
        setInputValue(question);
        handleSend(question);
    };

    const handleSend = async (questionText = null) => {
        const question = questionText || inputValue.trim();
        if (!question || isLoading) return;

        // Add user message
        setMessages(prev => [...prev, { text: question, isUser: true }]);
        setInputValue('');
        setIsLoading(true);

        try {
            // Call API
            const response = await fetch(`${API_BASE_URL}/api/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question }),
            });

            if (!response.ok) {
                // Try to extract error message from response
                let errorDetail = 'API request failed';
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorData.error || errorData.message || errorDetail;
                } catch (e) {
                    // If JSON parsing fails, use status text
                    errorDetail = response.statusText || errorDetail;
                }
                throw new Error(`${response.status}: ${errorDetail}`);
            }

            const data = await response.json();
            
            // Add assistant response
            setMessages(prev => [...prev, { 
                text: data.answer, 
                isUser: false,
                source: data.citation_link || null,
                timestamp: data.timestamp || null
            }]);
        } catch (error) {
            console.error('Error:', error);
            let errorMessage = 'Sorry, I encountered an error. Please try again later.';
            
            // Extract error message from error object
            const errorStr = error.message || error.toString();
            
            // More specific error messages
            if (errorStr.includes('Failed to fetch') || errorStr.includes('NetworkError')) {
                errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
            } else if (errorStr.includes('503') || errorStr.includes('RAG pipeline not initialized')) {
                errorMessage = 'The system is still initializing. Please wait a moment and try again.';
            } else if (errorStr.includes('404')) {
                errorMessage = 'API endpoint not found. Please check the server configuration.';
            } else if (errorStr.includes('500') || errorStr.includes('Error processing query')) {
                // Extract the actual error detail if available
                const match = errorStr.match(/500: (.+)/);
                if (match && match[1]) {
                    errorMessage = 'Server error: ' + match[1];
                } else {
                    errorMessage = 'Server error. Please try again later.';
                }
            } else if (errorStr.includes('Gemini API key') || errorStr.includes('GEMINI_API_KEY')) {
                errorMessage = 'Configuration error: API key not set. Please contact support.';
            } else if (errorStr.length > 0 && errorStr !== 'Error') {
                // Use the error message if it's informative
                errorMessage = errorStr.length > 100 ? errorStr.substring(0, 100) + '...' : errorStr;
            }
            
            setMessages(prev => [...prev, { 
                text: errorMessage, 
                isUser: false 
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const showWelcome = messages.length === 0 && !isLoading;

    return (
        <div className="chat-container">
            <div className="chat-header">
                <svg className="chat-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h1 className="chat-header-title">Mutual Fund Broww</h1>
            </div>
            
            <div className="chat-messages">
                {showWelcome ? (
                    <WelcomeState onQuestionClick={handleQuestionClick} />
                ) : (
                    <>
                        {messages.map((msg, index) => (
                            <MessageBubble 
                                key={index} 
                                message={msg.text} 
                                isUser={msg.isUser}
                                source={msg.source}
                                timestamp={msg.timestamp}
                            />
                        ))}
                        {isLoading && <LoadingBubble />}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            <div className="chat-input-area">
                <div className="input-container">
                    <input
                        ref={inputRef}
                        type="text"
                        className="chat-input"
                        placeholder="Ask a question..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                    />
                    <button
                        className="send-button"
                        onClick={() => handleSend()}
                        disabled={!inputValue.trim() || isLoading}
                    >
                        <svg className="send-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
}

// Render App
const rootElement = document.getElementById('root');
if (ReactDOM.createRoot) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(<ChatApp />);
} else {
    // Fallback for older React versions
    ReactDOM.render(<ChatApp />, rootElement);
}
"""

FRONTEND_STYLES_CSS = """/* Groww Brand Colors */
:root {
    --primary-green: #00B386;
    --light-green: #EBF9F5;
    --dark-text: #44475B;
    --secondary-text: #7C7E8C;
    --background: #FFFFFF;
    --user-bubble: #F9F9F9;
    --border: #EFEFEF;
}

/* Main Container */
.chat-container {
    width: 100%;
    max-width: 500px;
    height: 600px;
    background: var(--background);
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    overflow: hidden;
}

/* Header */
.chat-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 8px;
}

.chat-header-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--dark-text);
    margin: 0;
}

.chat-header-icon {
    width: 20px;
    height: 20px;
    color: var(--dark-text);
}

/* Chat Messages Area */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
    background: var(--background);
}

.chat-messages::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}

/* Welcome State */
.welcome-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 40px 20px;
    height: 100%;
}

.welcome-message {
    font-size: 14px;
    color: var(--dark-text);
    margin-bottom: 8px;
    line-height: 1.6;
}

.welcome-disclaimer {
    font-size: 12px;
    color: var(--secondary-text);
    margin-bottom: 24px;
}

.example-questions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
    max-width: 400px;
    margin-bottom: 20px;
}

.example-question-chip {
    padding: 10px 16px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--background);
    color: var(--primary-green);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
}

.example-question-chip:hover {
    background: var(--light-green);
    border-color: var(--primary-green);
}

/* Chat Bubbles */
.message-bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
}

.user-bubble {
    background: var(--user-bubble);
    color: var(--dark-text);
    align-self: flex-end;
    margin-left: auto;
}

.assistant-bubble {
    background: var(--light-green);
    color: var(--dark-text);
    align-self: flex-start;
}

.answer-text {
    margin-bottom: 8px;
}

.source-link {
    color: var(--primary-green);
    font-weight: 500;
    text-decoration: none;
    font-size: 14px;
    display: inline-block;
    margin-top: 8px;
}

.source-link:hover {
    text-decoration: underline;
}

.timestamp {
    font-size: 12px;
    color: var(--secondary-text);
    margin-top: 8px;
}

/* Loading State */
.loading-bubble {
    background: var(--light-green);
    align-self: flex-start;
    padding: 12px 16px;
    border-radius: 12px;
}

.loading-dots {
    display: flex;
    gap: 4px;
}

.loading-dot {
    width: 6px;
    height: 6px;
    background: var(--secondary-text);
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
}

.loading-dot:nth-child(1) {
    animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes bounce {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}

/* Input Area */
.chat-input-area {
    padding: 16px 20px;
    border-top: 1px solid var(--border);
    background: var(--background);
}

.input-container {
    display: flex;
    gap: 8px;
    align-items: center;
}

.chat-input {
    flex: 1;
    padding: 10px 16px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
    color: var(--dark-text);
    outline: none;
    transition: border-color 0.2s;
}

.chat-input:focus {
    border-color: var(--primary-green);
}

.chat-input::placeholder {
    color: var(--secondary-text);
}

.send-button {
    width: 40px;
    height: 40px;
    border: none;
    background: var(--primary-green);
    color: white;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
    flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
    background: #00A077;
}

.send-button:disabled {
    background: var(--border);
    cursor: not-allowed;
    opacity: 0.5;
}

.send-icon {
    width: 18px;
    height: 18px;
}

/* Empty State */
.empty-state {
    text-align: center;
    color: var(--secondary-text);
    font-size: 14px;
    padding: 20px;
}
"""

# Try to load from files (for local development), but use embedded versions as fallback
try:
    loaded_jsx = load_frontend_file("app.jsx")
    if loaded_jsx and len(loaded_jsx) > 100:  # Only use if substantial content
        FRONTEND_APP_JSX = loaded_jsx
        logger.info(f"Loaded app.jsx from file ({len(loaded_jsx)} chars)")
    else:
        logger.info(f"Using embedded app.jsx ({len(FRONTEND_APP_JSX)} chars)")
except Exception as e:
    logger.info(f"Using embedded app.jsx (file load failed: {e})")

try:
    loaded_css = load_frontend_file("styles.css")
    if loaded_css and len(loaded_css) > 100:  # Only use if substantial content
        FRONTEND_STYLES_CSS = loaded_css
        logger.info(f"Loaded styles.css from file ({len(loaded_css)} chars)")
    else:
        logger.info(f"Using embedded styles.css ({len(FRONTEND_STYLES_CSS)} chars)")
except Exception as e:
    logger.info(f"Using embedded styles.css (file load failed: {e})")

# Generate HTML with embedded frontend files (lazy generation to ensure files are loaded)
def get_frontend_html():
    """Get frontend HTML, reloading files if needed"""
    global FRONTEND_APP_JSX, FRONTEND_STYLES_CSS
    
    try:
        # If files weren't loaded, try again
        if not FRONTEND_APP_JSX or not FRONTEND_STYLES_CSS:
            logger.warning("Frontend files not loaded at startup, attempting to reload...")
            if not FRONTEND_APP_JSX:
                try:
                    FRONTEND_APP_JSX = load_frontend_file("app.jsx")
                except Exception as e:
                    logger.error(f"Error reloading app.jsx: {e}")
            if not FRONTEND_STYLES_CSS:
                try:
                    FRONTEND_STYLES_CSS = load_frontend_file("styles.css")
                except Exception as e:
                    logger.error(f"Error reloading styles.css: {e}")
        
        return generate_frontend_html(FRONTEND_APP_JSX, FRONTEND_STYLES_CSS)
    except Exception as e:
        logger.error(f"Error generating frontend HTML: {e}")
        # Return minimal HTML with error message
        return """<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
    <div style="padding: 20px; color: #44475B;">
        <p>Error loading frontend. Please check server logs.</p>
        <p style="font-size: 12px; color: #7C7E8C;">Error: """ + str(e) + """</p>
    </div>
</body>
</html>"""

# Generate initial HTML (will be regenerated on each request if needed)
try:
    FRONTEND_HTML = get_frontend_html()
except Exception as e:
    logger.error(f"Error generating initial frontend HTML: {e}")
    FRONTEND_HTML = """<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
    <div style="padding: 20px; color: #44475B;">
        <p>Error initializing frontend. Please check server logs.</p>
    </div>
</body>
</html>"""

from fastapi.responses import HTMLResponse, Response

# Serve frontend files
@app.get("/app.jsx")
async def serve_app_jsx():
    """Serve app.jsx"""
    if not FRONTEND_APP_JSX:
        raise HTTPException(status_code=500, detail="app.jsx not loaded")
    return Response(
        content=FRONTEND_APP_JSX, 
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )

@app.get("/styles.css")
async def serve_styles_css():
    """Serve styles.css"""
    if not FRONTEND_STYLES_CSS:
        raise HTTPException(status_code=500, detail="styles.css not loaded")
    return Response(
        content=FRONTEND_STYLES_CSS, 
        media_type="text/css",
        headers={"Cache-Control": "no-cache"}
    )

@app.get("/")
async def serve_frontend():
    """Serve frontend index.html at root"""
    try:
        # Regenerate HTML in case files weren't loaded at startup
        html = get_frontend_html()
        return HTMLResponse(
            content=html,
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        error_html = f"""<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body>
    <div style="padding: 20px; color: #44475B;">
        <p>Error loading frontend.</p>
        <p style="font-size: 12px; color: #7C7E8C;">Error: {str(e)}</p>
    </div>
</body>
</html>"""
        return HTMLResponse(content=error_html, status_code=200)

@app.get("/debug/frontend")
async def debug_frontend():
    """Debug endpoint to check frontend file loading"""
    return {
        "app_jsx_loaded": bool(FRONTEND_APP_JSX),
        "app_jsx_length": len(FRONTEND_APP_JSX) if FRONTEND_APP_JSX else 0,
        "styles_css_loaded": bool(FRONTEND_STYLES_CSS),
        "styles_css_length": len(FRONTEND_STYLES_CSS) if FRONTEND_STYLES_CSS else 0,
        "public_path_exists": public_path.exists(),
        "project_root": str(project_root),
        "public_path": str(public_path),
        "current_working_dir": str(Path.cwd())
    }


@app.get("/api/", response_model=dict)
async def api_root():
    """API root endpoint"""
    return {
        "message": "Mutual Fund FAQ Bot API",
        "version": "1.0.0",
        "endpoints": {
            "/api/query": "POST - Ask questions about mutual funds",
            "/api/schemes": "GET - List available mutual fund schemes",
            "/api/health": "GET - Health check",
            "/docs": "API documentation"
        }
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_funds(request: QueryRequest):
    """
    Query the mutual fund knowledge base
    
    Args:
        request: Query request with question and optional parameters
        
    Returns:
        QueryResponse with answer and sources
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    if not pipeline:
        # Return specific error message if available
        error_detail = rag_init_error or "RAG pipeline not initialized. Please check server logs."
        raise HTTPException(
            status_code=503,
            detail=error_detail
        )
    
    try:
        logger.info(f"Processing query: {request.question}")
        
        # Query RAG pipeline
        result = pipeline.query(
            question=request.question,
            fund_name=request.fund_name,
            top_k=request.top_k
        )
        
        # Convert sources to response format
        sources = [
            SourceInfo(
                fund_name=src['fund_name'],
                chunk_type=src['chunk_type'],
                similarity=src['similarity']
            )
            for src in result['sources']
        ]
        
        return QueryResponse(
            answer=result['answer'],
            sources=sources,
            confidence=result['confidence'],
            query=request.question,
            citation_link=result.get('citation_link', ''),
            timestamp=result.get('timestamp'),
            rejected=result.get('rejected', False),
            rejection_reason=result.get('rejection_reason')
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        # Return more specific error details
        error_detail = str(e)
        if "Gemini API key" in error_detail or "GEMINI_API_KEY" in error_detail:
            error_detail = "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        elif "not initialized" in error_detail.lower():
            error_detail = "RAG pipeline not initialized. Please check server logs."
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {error_detail}"
        )


@app.get("/api/schemes", response_model=FundsResponse)
async def list_schemes():
    """
    List all available mutual fund schemes
    
    Returns:
        FundsResponse with list of available funds
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    if not pipeline:
        error_detail = rag_init_error or "RAG pipeline not initialized"
        raise HTTPException(
            status_code=503,
            detail=error_detail
        )
    
    try:
        funds = pipeline.list_available_funds()
        
        fund_info = [
            {"name": fund, "available": True}
            for fund in funds
        ]
        
        return FundsResponse(
            funds=fund_info,
            total=len(fund_info)
        )
        
    except Exception as e:
        logger.error(f"Error listing schemes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing schemes: {str(e)}"
        )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse with system status
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    rag_initialized = pipeline is not None
    chunks_loaded = len(pipeline.chunks) if pipeline else 0
    funds_available = len(pipeline.list_available_funds()) if pipeline else 0
    
    status = "healthy" if pipeline else "unhealthy"
    
    return HealthResponse(
        status=status,
        rag_initialized=rag_initialized,
        chunks_loaded=chunks_loaded,
        funds_available=funds_available
    )


@app.get("/api/query/simple")
async def query_simple(question: str = Query(..., description="Question about mutual funds")):
    """
    Simple GET endpoint for queries (for easy testing)
    
    Args:
        question: User's question
        
    Returns:
        Simple JSON response with answer
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    if not pipeline:
        error_detail = rag_init_error or "RAG pipeline not initialized"
        raise HTTPException(
            status_code=503,
            detail=error_detail
        )
    
    try:
        result = pipeline.query(question=question)
        return {
            "question": question,
            "answer": result['answer'],
            "confidence": result['confidence']
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

