from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, MemoryResponse
from therapy_service import process_therapy_chat, get_session_history, get_session_memories, create_therapy_session

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Therapy Webapp API is running", "status": "healthy"}

@api_router.post("/therapy/chat", response_model=ChatResponse)
async def therapy_chat(request: ChatRequest):
    """Main therapy chat endpoint"""
    try:
        return await process_therapy_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing therapy session: {str(e)}")

@api_router.get("/therapy/session/{session_id}/history")
async def get_therapy_session_history(session_id: str):
    """Get conversation history for a session"""
    try:
        return await get_session_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session history: {str(e)}")

@api_router.post("/therapy/session")
async def create_new_therapy_session():
    """Create a new therapy session"""
    try:
        session_id = await create_therapy_session()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating therapy session: {str(e)}")

@api_router.get("/therapy/memories/{session_id}", response_model=MemoryResponse)
async def get_memories_for_session(session_id: str, query: str = ""):
    """Debug endpoint to test memory retrieval"""
    try:
        return await get_session_memories(session_id, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memories: {str(e)}")