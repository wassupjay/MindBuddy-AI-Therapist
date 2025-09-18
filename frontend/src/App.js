import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { motion } from "framer-motion";
import { Send } from "lucide-react";
import axios from "axios";

const API_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

//Message component
const Message = ({ text, isUser }) => (
  <motion.div 
    className={`message ${isUser ? 'user-message' : 'ai-message'}`}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
  >
    {text}
  </motion.div>
);

//Typing indicator
const TypingIndicator = () => (
  <div className="typing-indicator">
    <div className="typing-dot"></div>
    <div className="typing-dot"></div>
    <div className="typing-dot"></div>
  </div>
);

function App() {
  // State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Refs
  const messagesEnd = useRef(null);
  
  // Initialize
  useEffect(() => {
    addWelcomeMessage();
  }, []);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const addWelcomeMessage = () => {
    setTimeout(() => {
      setMessages([{
        id: 1,
        text: "Hi! I'm your AI therapy companion. How are you feeling today?",
        isUser: false
      }]);
    }, 1000);
  };
  
  const scrollToBottom = () => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage = {
      id: Date.now(),
      text: input,
      isUser: true
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_URL}/api/therapy/chat`, {
        message: input,
        session_id: sessionId
      });
      
      const aiMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        isUser: false
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }
      
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting. Please try again.",
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setLoading(false);
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div>
            <h1 className="app-title">MindBuddy</h1>
            <p className="app-subtitle">Your AI Therapy Companion</p>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="main-content">
        <div className="chat-container">
          <div className="messages">
            {messages.map(msg => (
              <Message key={msg.id} text={msg.text} isUser={msg.isUser} />
            ))}
            {loading && <TypingIndicator />}
            <div ref={messagesEnd} />
          </div>
          
          <div className="input-area">
            <textarea
              className="message-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              rows="1"
            />
            
            <button
              className="send-button"
              onClick={sendMessage}
              disabled={!input.trim() || loading}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
        
        <p className="footer-text">
          I'm a safe, private, and judgment-free space for you
        </p>
      </main>
    </div>
  );
}

export default App;
