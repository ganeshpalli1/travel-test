#!/usr/bin/env python3
"""
FastAPI Backend for Digital Nomad Travel Chatbot
Vercel-optimized version
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json

# Import our travel chatbot
from travel_assistant import TravelChatbot

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(
    title="Digital Nomad Travel Assistant API",
    description="Get excited, direct travel answers for digital nomads! 🌍",
    version="1.0.0"
)

# Global chatbot instance
chatbot = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

def initialize_chatbot():
    """Initialize the chatbot"""
    global chatbot
    
    if chatbot is None:
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            raise RuntimeError("PERPLEXITY_API_KEY environment variable is required")
        
        chatbot = TravelChatbot(api_key)
        print("🚀 Travel Chatbot initialized and ready!")
    
    return chatbot

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the main chat interface"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head><title>Travel Assistant</title></head>
        <body>
            <h1>🌍 Digital Nomad Travel Assistant</h1>
            <p>Static files not found. Please ensure static folder is deployed.</p>
        </body>
        </html>
        """)

@app.get("/static/{file_path:path}")
async def get_static_files(file_path: str):
    """Serve static files"""
    try:
        static_file_path = f"static/{file_path}"
        if os.path.exists(static_file_path):
            return FileResponse(static_file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - sends user message to travel assistant
    """
    try:
        # Initialize chatbot if needed
        current_chatbot = initialize_chatbot()
        
        if not request.message.strip():
            return ChatResponse(
                response="💭 I'm ready when you are! Ask me anything about travel!",
                success=True
            )
        
        # Get response from chatbot (no progress indicator for API)
        response = current_chatbot.chat(request.message, show_progress=False)
        
        return ChatResponse(response=response, success=True)
        
    except Exception as e:
        return ChatResponse(
            response="Oops! Something went wrong. Try again? 🤔",
            success=False,
            error=str(e)
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        current_chatbot = initialize_chatbot()
        chatbot_ready = current_chatbot is not None
    except Exception:
        chatbot_ready = False
    
    return {
        "status": "healthy",
        "chatbot_ready": chatbot_ready,
        "message": "🌍 Travel Assistant API is running!",
        "environment": "vercel" if os.getenv("VERCEL") else "local"
    }

@app.get("/api/stats")
async def get_stats():
    """Get conversation statistics"""
    try:
        current_chatbot = initialize_chatbot()
        return {
            "total_conversations": len(current_chatbot.conversation_history),
            "last_activity": current_chatbot.conversation_history[-1].timestamp if current_chatbot.conversation_history else None
        }
    except Exception:
        return {"error": "Chatbot not initialized"}

# For Vercel serverless functions
handler = app

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 