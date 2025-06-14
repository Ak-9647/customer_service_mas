import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "👋 Hello! I'm your AI customer support assistant. I'm here to help you with order inquiries, refunds, shipping questions, and more. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date(),
      suggestions: [
        "Check order status",
        "Process a refund", 
        "Shipping information",
        "Return policy",
        "Contact information"
      ]
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: textToSend,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: textToSend }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Simulate typing delay for better UX
      setTimeout(() => {
        setIsTyping(false);
        const botMessage = {
          id: Date.now() + 1,
          text: data.response || 'Sorry, I encountered an error processing your request.',
          sender: 'bot',
          timestamp: new Date(),
          // Parse suggestions from backend if available
          suggestions: data.suggestions || (data.category ? getSuggestionsForCategory(data.category) : null),
          category: data.category,
          agent: data.routed_to
        };
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
      }, 1000 + Math.random() * 1000); // Random delay between 1-2 seconds

    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I\'m having trouble connecting right now. Please try again in a moment.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        text: "👋 Hello! I'm your AI customer support assistant. I'm here to help you with order inquiries, refunds, shipping questions, and more. How can I assist you today?",
        sender: 'bot',
        timestamp: new Date(),
        suggestions: [
          "Check order status",
          "Process a refund", 
          "Shipping information",
          "Return policy",
          "Contact information"
        ]
      }
    ]);
    setInputMessage('');
  };

  const formatMessage = (text) => {
    // Convert markdown-style formatting to HTML
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br/>');
  };

  const getSuggestionsForCategory = (category) => {
    const categoryMap = {
      'shipping': [
        'How much does shipping cost?',
        'When will my order arrive?',
        'Track my order',
        'International shipping'
      ],
      'refund_policy': [
        'Start a refund for order 12345',
        'How long do refunds take?',
        'What can I return?',
        'Exchange an item'
      ],
      'returns': [
        'How do I return an item?',
        'Get a return label',
        'Return status',
        'Exchange policy'
      ],
      'payment': [
        'Payment not working',
        'Update payment method',
        'Billing question',
        'Payment security'
      ],
      'contact': [
        'Phone number',
        'Email support',
        'Business hours',
        'Live chat'
      ],
      'account': [
        'Reset password',
        'Update email',
        'Change address',
        'Account settings'
      ]
    };
    return categoryMap[category] || null;
  };

  const quickActions = [
    { icon: '📦', text: 'Check order 12345', color: 'blue' },
    { icon: '💰', text: 'I want a refund for order 12345', color: 'green' },
    { icon: '🚚', text: 'Shipping information', color: 'purple' },
    { icon: '🔄', text: 'Return policy', color: 'orange' },
    { icon: '💳', text: 'Payment methods', color: 'teal' },
    { icon: '📞', text: 'Contact information', color: 'red' },
  ];

  return (
    <div className="app">
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="agent-avatar">
              <div className="avatar-circle">
                <span className="avatar-icon">🤖</span>
              </div>
              <div className="status-indicator online"></div>
            </div>
            <div className="agent-info">
              <h1 className="agent-name">AI Customer Support</h1>
              <p className="agent-status">
                <span className="status-dot"></span>
                Online • Ready to help
              </p>
            </div>
          </div>
          <div className="header-actions">
            <button className="action-btn" title="Clear chat" onClick={clearChat}>
              <span>🗑️</span>
            </button>
            <button className="action-btn" title="Settings">
              <span>⚙️</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-container">
          <div className="messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-content">
                  {message.sender === 'bot' && (
                    <div className="message-avatar">
                      <span>🤖</span>
                    </div>
                  )}
                  <div className={`message-bubble ${message.isError ? 'error' : ''}`}>
                    <div 
                      className="message-text"
                      dangerouslySetInnerHTML={{ __html: formatMessage(message.text) }}
                    />
                    {message.suggestions && (
                      <div className="suggestions">
                        {message.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            className="suggestion-chip"
                            onClick={() => handleSendMessage(suggestion)}
                            disabled={isLoading}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                    <div className="message-time">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                  {message.sender === 'user' && (
                    <div className="message-avatar user">
                      <span>👤</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot">
                <div className="message-content">
                  <div className="message-avatar">
                    <span>🤖</span>
                  </div>
                  <div className="message-bubble typing">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Quick Actions */}
        {messages.length <= 1 && (
          <div className="quick-actions">
            <h3>Quick Actions</h3>
            <div className="action-grid">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className={`quick-action-btn ${action.color}`}
                  onClick={() => handleSendMessage(action.text)}
                  disabled={isLoading}
                >
                  <span className="action-icon">{action.icon}</span>
                  <span className="action-text">{action.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="message-input"
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              className="send-button"
            >
              {isLoading ? (
                <div className="loading-spinner"></div>
              ) : (
                <span>🚀</span>
              )}
            </button>
          </div>
          <div className="input-footer">
            <span className="powered-by">
              Powered by ADK AI • Press Enter to send
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
