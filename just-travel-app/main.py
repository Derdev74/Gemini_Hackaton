"""
Just Travel App - Backend API & Agent Manager
=============================================

This module serves as the "Antigravity Agent Manager" (Orchestrator).
It uses FastAPI to expose endpoints and the Google ADK (or internal logic)
to manage the lifecycle and workflow of the specialist agents.

Workflow:
1. Profiler (Sequential) -> Captures state
2. Research (Parallel) -> PathFinder + TrendSpotter + Concierge
3. Optimizer (Sequential) -> Synthesizes final plan
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# FastAPI & Rate Limiting
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import specialist agents
from agents.profiler import ProfilerAgent
from agents.pathfinder import PathfinderAgent
from agents.trend_spotter import TrendSpotterAgent
from agents.concierge import ConciergeAgent
from agents.optimizer import OptimizerAgent
from agents.creative_director import CreativeDirectorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AgentManager")

# Load env vars
load_dotenv()

# --- Rate Limiter Setup ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Just Travel Agent API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files for generated assets and uploads
# This matches: frontend/public -> mapped to local paths
# In Next.js dev mode, Next serves public/. But we are writing there.
# To be safe and see them immediately if Next.js doesn't HMR static files well (it usually does),
# we don't strictly need to serve them via FastAPI if the Frontend component links to them relative to root.
# However, if we wanted to serve them via API:
# app.mount("/static", StaticFiles(directory="frontend/public"), name="static")
# For now, we rely on Next.js serving them from its public folder.

# --- CORS Setup ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Upload Validation ---
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
# Magic bytes for common image formats
IMAGE_SIGNATURES = [b'\x89PNG', b'\xff\xd8\xff', b'GIF87a', b'GIF89a']

# --- Data Models ---
class ChatRequest(BaseModel):
    message: str
    preferences: Optional[Dict[str, Any]] = {}
    uploaded_file: Optional[str] = None

class AgentResponse(BaseModel):
    agent: str
    status: str
    message: str
    profile: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    creative: Optional[Dict[str, Any]] = None

# --- Antigravity Agent Manager (Orchestrator) ---
class AntigravityAgentManager:
    """
    Central orchestrator that manages the specialized agents.
    Implements the Deterministic Workflow: Seq -> Par -> Seq.
    """
    def __init__(self):
        logger.info("Initializing Antigravity Agent Manager...")
        
        # Initialize Workers
        self.profiler = ProfilerAgent()
        self.pathfinder = PathfinderAgent()
        self.trend_spotter = TrendSpotterAgent()
        self.concierge = ConciergeAgent()
        self.optimizer = OptimizerAgent()
        self.creative_director = CreativeDirectorAgent()
        
        logger.info("Agents armed and ready.")

    async def run_workflow(self, user_message: str, current_context: Dict) -> AgentResponse:
        """
        Executes the intelligent travel planning workflow.
        """
        logger.info(f"Processing message: {user_message}")
        
        # --- Step 1: Profiling (Sequential) ---
        # Any interaction passes through the profiler first to update state
        profile_result = await self.profiler.async_process(user_message, current_context)
        
        # Update context with new profile data
        updated_profile = profile_result.get("profile", {})
        current_context.update({"profile": updated_profile})
        
        # If the profiler needs more info or if it was just a simple chat, return early
        # We check if we have enough "signals" to proceed to research
        if not self._should_trigger_research(user_message, updated_profile):
            follow_ups = profile_result.get("follow_up_questions", [])
            changes = profile_result.get("extracted_preferences", [])
            message = "\n".join(follow_ups) if follow_ups else (changes[0] if changes else "Tell me more about your trip!")
            return AgentResponse(
                agent="profiler",
                status="success",
                message=message,
                profile=updated_profile
            )

        # --- Step 2: Research (Parallel) ---
        logger.info("Triggering Parallel Research Phase...")
        
        # Define tasks
        destination = updated_profile.get("destination") or current_context.get("destination") or "Paris"
        
        task_pathfinder = self.pathfinder.async_process(destination, current_context)
        task_trends = self.trend_spotter.async_process(f"trends in {destination}", current_context)
        task_concierge = self.concierge.async_process(destination, current_context)
        
        # Run in parallel
        results = await asyncio.gather(task_pathfinder, task_trends, task_concierge, return_exceptions=True)
        
        path_data, trend_data, concierge_data = results
        
        # --- Step 3: Optimization (Sequential) ---
        logger.info("Synthesizing Research into Itinerary...")
        
        synthesis_context = {
            "profile": updated_profile,
            "destinations": path_data.get("results", []) if not isinstance(path_data, Exception) else [],
            "trends": trend_data.get("trends", []) if not isinstance(trend_data, Exception) else [],
            "accommodations": concierge_data.get("results", []) if not isinstance(concierge_data, Exception) else []
        }
        
        final_plan = await self.optimizer.async_process("generate itinerary", synthesis_context)
        
        # --- Step 4: Creative Director (Sequential) ---
        # Generate visuals for the final plan
        logger.info("Lights, Camera, Action! Calling Creative Director...")
        
        # Check if there was an uploaded file in the message
        # In a real app, we'd pass this strictly, but here we can check the context
        
        creative_assets = await self.creative_director.async_process(final_plan, current_context)
        
        return AgentResponse(
            agent="optimizer",
            status="success",
            message=final_plan.get("summary", "Here is your plan!"),
            profile=updated_profile,
            data={"itinerary": final_plan},
            creative=creative_assets
        )

    def _should_trigger_research(self, message: str, profile: Dict) -> bool:
        """Heuristic: trigger research when the message signals trip-planning intent."""
        keywords = ["plan", "itinerary", "go to", "trip", "book", "schedule", "travel", "visit", "fly", "destination"]
        return any(k in message.lower() for k in keywords)

# Initialize Manager Instance
agent_manager = AntigravityAgentManager()

# --- API Endpoints ---

@app.get("/api/health")
async def health_check():
    return {"status": "online", "manager": "AntigravityAgentManager"}

@app.post("/api/chat", response_model=AgentResponse)
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    """
    Main chat endpoint.
    """
    try:
        # Inject uploaded_file into context if present
        if chat_req.uploaded_file:
            chat_req.preferences["uploaded_file"] = chat_req.uploaded_file

        response = await agent_manager.run_workflow(chat_req.message, chat_req.preferences)
        return response
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing your request.")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle file uploads with server-side validation.
    """
    import time

    # --- Extension check ---
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed. Supported: PNG, JPG, GIF, WEBP")

    # --- Read & size check ---
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds the 10 MB size limit.")

    # --- Magic-bytes check ---
    is_valid = any(content.startswith(sig) for sig in IMAGE_SIGNATURES)
    if not is_valid and len(content) >= 12:
        is_valid = content[:4] == b'RIFF' and content[8:12] == b'WEBP'  # WEBP
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    try:
        upload_dir = os.path.join(os.getcwd(), "frontend", "public", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        timestamp = int(time.time())
        clean_name = "".join(x for x in (file.filename or "upload") if x.isalnum() or x in "._-")
        filename = f"{timestamp}_{clean_name}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return {"url": f"/uploads/{filename}", "filename": filename}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed.")


@app.get("/api/proxy/photo")
async def proxy_photo(ref: str = Query(...)):
    """
    Proxy Google Maps photo requests so the API key never reaches the client.
    """
    import requests as _req

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key or not ref:
        raise HTTPException(status_code=400, detail="Missing parameters.")

    url = (
        f"https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth=400&photoreference={ref}&key={api_key}"
    )
    try:
        resp = await asyncio.to_thread(_req.get, url, timeout=10, stream=True)
        resp.raise_for_status()
        return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
    except Exception as e:
        logger.error(f"Photo proxy failed: {e}")
        raise HTTPException(status_code=502, detail="Photo fetch failed.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
