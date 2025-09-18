import asyncio
import uuid
import re
from datetime import datetime
from typing import List
from openai import AsyncOpenAI
from pinecone import Pinecone

from config import (
    OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX, 
    EMBEDDING_MODEL, CHAT_MODEL, EMBEDDING_DIMENSION,
    MEMORY_THRESHOLD_CURRENT_SESSION, MEMORY_THRESHOLD_CROSS_SESSION,
    MEMORY_SCORE_THRESHOLD
)
from prompts import get_conversation_evaluation_prompt

# Initialize clients
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Global variable for Pinecone index
pinecone_index = None

async def initialize_pinecone():
    """Initialize Pinecone index on startup"""
    global pinecone_index
    try:
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        
        if PINECONE_INDEX not in existing_indexes:
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
            )
            print(f"Created Pinecone index: {PINECONE_INDEX}")
        
        pinecone_index = pc.Index(PINECONE_INDEX)
        print(f"Connected to Pinecone index: {PINECONE_INDEX}")
        
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")

async def get_relevant_memories(query: str, session_id: str, limit: int = 5) -> List[str]:
    """Retrieve relevant conversation memories from Pinecone across all sessions"""
    if not pinecone_index:
        return []
    
    try:
        # Create embedding for the query
        embedding_response = await openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Search current session memories
        current_session_response = pinecone_index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            filter={"session_id": session_id}
        )
        
        # Search all sessions memories
        all_sessions_response = pinecone_index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True
        )
        
        memories = []
        
        # Process current session memories first
        for match in current_session_response.matches:
            if match.score > MEMORY_THRESHOLD_CURRENT_SESSION:
                conversation = match.metadata.get("conversation", "")
                if conversation and conversation not in memories:
                    memories.append(f"[Current session] {conversation}")
        
        # Process memories from other sessions
        for match in all_sessions_response.matches:
            if match.score > MEMORY_THRESHOLD_CROSS_SESSION:
                conversation = match.metadata.get("conversation", "")
                match_session_id = match.metadata.get("session_id", "")
                
                if (conversation and 
                    conversation not in [m.replace("[Current session] ", "") for m in memories] and 
                    match_session_id != session_id):
                    memories.append(f"[Previous conversation] {conversation}")
        
        return memories[:limit]
        
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        return []

async def is_conversation_worth_storing(user_message: str, ai_response: str) -> bool:
    """Use LLM to evaluate if a conversation contains meaningful therapeutic content"""
    try:
        # Skip obviously trivial cases to save API calls
        if len(user_message.strip()) < 5 or len(ai_response.strip()) < 10:
            return False
        
        evaluation_prompt = get_conversation_evaluation_prompt(user_message, ai_response)
        
        # Get LLM evaluation
        evaluation_response = await openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": evaluation_prompt}],
            max_tokens=10,
            temperature=0.1
        )
        
        score_text = evaluation_response.choices[0].message.content.strip()
        
        # Extract numeric score
        score_match = re.search(r'\b([0-9]|10)\b', score_text)
        if score_match:
            score = int(score_match.group(1))
            
            if score >= MEMORY_SCORE_THRESHOLD:
                print(f"Storing conversation - LLM Score: {score}/10")
            else:
                print(f"Skipping conversation - LLM Score: {score}/10")
            
            return score >= MEMORY_SCORE_THRESHOLD
        else:
            print(f"Could not parse LLM score: {score_text} - defaulting to STORE")
            return True
            
    except Exception as e:
        print(f"Error in LLM conversation evaluation: {e} - defaulting to STORE")
        return True

async def store_conversation_memory(session_id: str, conversation: str, user_id: str = None):
    """Store conversation in Pinecone for long-term memory"""
    if not pinecone_index:
        return
    
    try:
        # Create embedding
        embedding_response = await openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=conversation
        )
        embedding = embedding_response.data[0].embedding
        
        # Generate user_id if not provided
        if not user_id:
            user_id = f"user_{session_id.split('_')[0] if '_' in session_id else session_id[:8]}"
        
        # Store in Pinecone
        vector_id = f"{session_id}_{uuid.uuid4()}"
        metadata = {
            "session_id": session_id,
            "user_id": user_id,
            "conversation": conversation,
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_length": len(conversation),
            "topics": extract_conversation_topics(conversation)
        }
        
        pinecone_index.upsert([{
            "id": vector_id,
            "values": embedding,
            "metadata": metadata
        }])
        
        print(f"Stored memory for session {session_id[:8]}... with {len(conversation)} characters")
        
    except Exception as e:
        print(f"Error storing memory: {e}")

def extract_conversation_topics(conversation: str) -> str:
    """Extract key topics from conversation for better memory retrieval"""
    try:
        therapy_keywords = [
            'anxiety', 'depression', 'stress', 'work', 'job', 'relationship', 'family',
            'sleep', 'panic', 'worry', 'fear', 'angry', 'sad', 'overwhelmed', 'therapy',
            'counseling', 'medication', 'interview', 'presentation', 'public speaking',
            'social', 'friends', 'marriage', 'divorce', 'grief', 'loss', 'trauma'
        ]
        
        conversation_lower = conversation.lower()
        found_topics = [keyword for keyword in therapy_keywords if keyword in conversation_lower]
        
        return ', '.join(found_topics[:5])
    except:
        return ""