const { useState, useEffect, useRef } = React;

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
                throw new Error('API request failed');
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
            
            // More specific error messages
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                errorMessage = 'Unable to connect to the server. Please make sure the backend API is running on http://localhost:8000';
            } else if (error.message.includes('404')) {
                errorMessage = 'API endpoint not found. Please check the backend server configuration.';
            } else if (error.message.includes('500')) {
                errorMessage = 'Server error. Please try again later.';
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

