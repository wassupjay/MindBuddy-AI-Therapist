# MindBuddy - AI Therapy Companion

A sophisticated AI therapy chatbot application that provides empathetic conversational support with intelligent memory management.

## 🌟 Features

- **AI-Powered Therapy Chat**: Conversations powered by OpenAI GPT-4
- **Long-term Memory**: Pinecone vector database for cross-session memory
- **Intelligent Filtering**: LLM-based conversation importance evaluation
- **Beautiful UI**: Modern, responsive interface with custom logo
- **Session Management**: Persistent conversation history
- **Secure**: Environment-based configuration for API keys

## 🏗️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database for session storage
- **Pinecone**: Vector database for long-term memory
- **OpenAI GPT-4**: AI conversation engine
- **Motor**: Async MongoDB driver

### Frontend
- **React**: Modern JavaScript framework
- **Framer Motion**: Smooth animations
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client for API calls
- **Lucide Icons**: Beautiful icon set

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud)
- OpenAI API key
- Pinecone API key

## Open two terminals, one for frontend and one for backend.

### Backend Setup
1. **Navigate to backend folder**
   ```bash
   cd backend
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   MONGO_URL=mongodb://localhost:27017/aitherapist
   ```
4. **Start the server**
   ```bash
   python -m uvicorn server:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend folder**
   ```bash
   cd frontend
   ```
2. **Install dependencies**
   ```bash
   npm install
   ```
3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
4. **Start the frontend**
   ```bash
   npm start
   ```

## 📝 Configuration

### Required API Keys

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Pinecone API Key**: Get from [Pinecone Console](https://app.pinecone.io/)
3. **MongoDB**: Local installation or [MongoDB Atlas](https://www.mongodb.com/atlas)

### Environment Variables

**Backend (.env)**:
```env
MONGO_URL=mongodb://localhost:27017/aitherapist
DB_NAME=aitherapist
CORS_ORIGINS=*
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX=mychatbot
```

**Frontend (.env)**:
```env
REACT_APP_BACKEND_URL=http://localhost:8000
WDS_SOCKET_PORT=0
```

## 🏃‍♂️ Development

### Backend Development
```bash
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

## 📦 Deployment

### Backend Deployment
- Update environment variables for production
- Use production MongoDB instance
- Configure CORS_ORIGINS for your domain

### Frontend Deployment
- Update REACT_APP_BACKEND_URL to your production backend URL
- Build: `npm run build`
- Deploy the `build` folder to your hosting service

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for the GPT-4 API
- Pinecone for vector database services
- React and FastAPI communities