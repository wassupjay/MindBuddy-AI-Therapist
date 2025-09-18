import asyncio
import uuid
from typing import List, Dict
from openai import AsyncOpenAI
from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL, DB_NAME, OPENAI_API_KEY, CHAT_MODEL, MAX_TOKENS, TEMPERATURE, MAX_CONVERSATION_HISTORY
from models import TherapyMessage, TherapySession, ChatRequest, ChatResponse, MemoryResponse
from prompts import get_therapy_system_prompt
from memory_service import get_relevant_memories, is_conversation_worth_storing, store_conversation_memory

# Initialize clients
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

async def process_therapy_chat(request: ChatRequest) -> ChatResponse:
    """Process therapy chat request and return AI response"""
    try:
        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Store user message
        user_message = TherapyMessage(
            session_id=session_id,
            role="user",
            content=request.message
        )
        await db.therapy_messages.insert_one(user_message.dict())
        
        # Get conversation history
        recent_messages = await db.therapy_messages.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(MAX_CONVERSATION_HISTORY).to_list(MAX_CONVERSATION_HISTORY)
        
        recent_messages.reverse()
        
        # Build conversation context
        conversation_history = []
        for msg in recent_messages:
            conversation_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Get relevant memories
        relevant_memories = await get_relevant_memories(request.message, session_id)
        memory_context = ""
        if relevant_memories:
            memory_context = "\n\nRelevant context from previous conversations:\n" + "\n".join([f"- {memory}" for memory in relevant_memories])
            memory_context += "\n\nPlease reference these previous conversations when relevant to provide continuity and deeper understanding."
        
        # Create system prompt
        system_prompt = get_therapy_system_prompt(memory_context)
        
        # Prepare messages for AI
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        
        # Get AI response
        completion = await openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        
        ai_response = completion.choices[0].message.content
        
        # Store AI response
        ai_message = TherapyMessage(
            session_id=session_id,
            role="assistant",
            content=ai_response
        )
        await db.therapy_messages.insert_one(ai_message.dict())
        
        # Store conversation in Pinecone if meaningful
        if await is_conversation_worth_storing(request.message, ai_response):
            asyncio.create_task(store_conversation_memory(
                session_id, 
                f"User: {request.message}\nTherapist: {ai_response}",
                user_id=session_id
            ))
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            message_id=ai_message.id
        )
        
    except Exception as e:
        print(f"Error in therapy chat: {e}")
        raise e

async def get_session_history(session_id: str) -> Dict:
    """Get conversation history for a session"""
    try:
        messages = await db.therapy_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(100)
        
        return {"messages": messages}
    except Exception as e:
        print(f"Error getting session history: {e}")
        raise e

async def get_session_memories(session_id: str, query: str = "") -> MemoryResponse:
    """Get memories for debugging purposes"""
    try:
        if not query:
            query = "anxiety stress work therapy"
        
        memories = await get_relevant_memories(query, session_id, limit=10)
        return MemoryResponse(
            session_id=session_id,
            query=query,
            memories=memories,
            count=len(memories)
        )
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        raise e

async def create_therapy_session() -> str:
    """Create a new therapy session and store it in database"""
    try:
        session = TherapySession()
        await db.therapy_sessions.insert_one(session.dict())
        return session.id
    except Exception as e:
        print(f"Error creating session: {e}")
        raise e

async def close_db_connection():
    """Close database connection"""
    mongo_client.close()