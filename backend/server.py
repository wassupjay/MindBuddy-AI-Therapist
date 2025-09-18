from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging

from config import CORS_ORIGINS
from routes import api_router
from memory_service import initialize_pinecone
from therapy_service import close_db_connection

# Create the main app
app = FastAPI(title="AI Therapy Webapp", description="Interactive AI therapy with conversation memory")

# Include API routes
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS.split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_pinecone()
    logger.info("AI Therapy Webapp started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_db_connection()
    logger.info("AI Therapy Webapp shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)