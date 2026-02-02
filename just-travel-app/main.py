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
from fastapi import FastAPI, Request, HTTPException, Depends
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

# --- Data Models ---
class ChatRequest(BaseModel):
    message: str
    preferences: Optional[Dict[str, Any]] = {}

class AgentResponse(BaseModel):
    agent: str
    status: str
    message: str
    profile: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

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
            return AgentResponse(
                agent="profiler",
                status="success",
                message=profile_result.get("extracted_preferences", [""])[0] or "Tell me more about your trip!",
                profile=updated_profile
            )

        # --- Step 2: Research (Parallel) ---
        logger.info("Triggering Parallel Research Phase...")
        
        # Define tasks
        destination = current_context.get("destination", "Paris") # Default or extracted
        
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
            "destinations": path_data if not isinstance(path_data, Exception) else [],
            "trends": trend_data if not isinstance(trend_data, Exception) else [],
            "accommodations": concierge_data if not isinstance(concierge_data, Exception) else []
        }
        
        final_plan = await self.optimizer.async_process("generate itinerary", synthesis_context)
        
        return AgentResponse(
            agent="optimizer",
            status="success",
            message=final_plan.get("summary", "Here is your plan!"),
            profile=updated_profile,
            data={"itinerary": final_plan}
        )

    def _should_trigger_research(self, message: str, profile: Dict) -> bool:
        """Heuristic to decide if we should move from chatting to planning."""
        keywords = ["plan", "itinerary", "go to", "trip", "book", "schedule"]
        return any(k in message.lower() for k in keywords) and len(profile.get("interests", [])) > 0

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
        response = await agent_manager.run_workflow(chat_req.message, chat_req.preferences)
        return response
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
