import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment Variables
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
PINECONE_INDEX = os.environ['PINECONE_INDEX']
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# API Configuration
MAX_TOKENS = 500
TEMPERATURE = 0.7
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_DIMENSION = 1536

# Memory Configuration
MEMORY_THRESHOLD_CURRENT_SESSION = 0.6
MEMORY_THRESHOLD_CROSS_SESSION = 0.5
MEMORY_SCORE_THRESHOLD = 6
MAX_MEMORIES = 5
MAX_CONVERSATION_HISTORY = 10