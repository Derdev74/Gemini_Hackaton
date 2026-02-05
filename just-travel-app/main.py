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
import uuid
from typing import Optional, Dict, Any
from datetime import timedelta
from dotenv import load_dotenv

# FastAPI & Rate Limiting
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, Query, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

# Import specialist agents
from agents.profiler import ProfilerAgent
from agents.pathfinder import PathfinderAgent
from agents.trend_spotter import TrendSpotterAgent
from agents.concierge import ConciergeAgent
from agents.optimizer import OptimizerAgent
from agents.creative_director import CreativeDirectorAgent

# Import DB and Auth
from database import init_db, get_session, User, Itinerary
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

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

# --- Startup Event ---
@app.on_event("startup")
async def on_startup():
    await init_db()

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
IMAGE_SIGNATURES = [b'\x89PNG', b'\xff\xd8\xff', b'GIF87a', b'GIF89a']

# --- Data Models ---
class ChatRequest(BaseModel):
    message: str
    preferences: Dict[str, Any] = {}
    uploaded_file: Optional[str] = None

class AgentResponse(BaseModel):
    agent: str
    status: str
    message: str
    profile: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    creative: Optional[Dict[str, Any]] = None

class SaveItineraryRequest(BaseModel):
    destination: str
    summary: str
    itinerary_data: Dict[str, Any] = {}
    creative_assets: Dict[str, Any] = {}

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]

# --- Auth Dependency ---
async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Get current user from HttpOnly Access Token cookie.
    If missing or expired, Frontend should call /refresh endpoint (handled by UI logic).
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_token(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if not email:
         raise HTTPException(status_code=401, detail="Invalid token subject")
         
    # Check if user exists in DB
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user

async def get_optional_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Like get_current_user but returns None instead of raising 401."""
    if not access_token:
        return None
    payload = verify_token(access_token)
    if not payload or payload.get("type") != "access":
        return None
    email = payload.get("sub")
    if not email:
        return None
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalars().first()

def _set_auth_cookies(response: Response, email: str):
    """Set access and refresh token cookies on a response."""
    access_token = create_access_token({"sub": email})
    refresh_token = create_refresh_token({"sub": email})
    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, samesite="lax", secure=False,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, samesite="lax", secure=False,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

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
        """Heuristic: trigger research when the message signals trip-planning intent or a destination is set."""
        keywords = ["plan", "itinerary", "go to", "trip", "book", "schedule", "travel", "visit", "fly", "destination"]
        has_keyword = any(k in message.lower() for k in keywords)
        has_destination = bool(profile.get("destination"))
        return has_keyword or has_destination

# Initialize Manager Instance
agent_manager = AntigravityAgentManager()

# --- API Endpoints ---

@app.post("/api/auth/register", response_model=UserRead)
@limiter.limit("5/hour")
async def register(
    request: Request,
    response: Response,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """Register a new user (Email/Password) and log them in."""
    # Check if exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create User
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        provider="local"
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    _set_auth_cookies(response, new_user.email)
    return new_user

@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    """Login with credentials and set HttpOnly cookies."""
    statement = select(User).where(User.email == credentials.email)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if not user or not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    _set_auth_cookies(response, user.email)
    return {"message": "Login successful", "user": {"email": user.email, "full_name": user.full_name}}

@app.post("/api/auth/refresh")
async def refresh_token_endpoint(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(get_session)
):
    """Refresh the access token using the refresh token cookie."""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    email = payload.get("sub")
    
    # Check user existence (optional but good security)
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    if not result.scalars().first():
         raise HTTPException(status_code=401, detail="User not found")
    
    # Issue new access token
    new_access_token = create_access_token({"sub": email})
    
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message": "Token refreshed"}

class GoogleAuthRequest(BaseModel):
    id_token: str

@app.post("/api/auth/google")
@limiter.limit("5/minute")
async def google_auth(
    request: Request,
    response: Response,
    auth_req: GoogleAuthRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Exchange Google ID Token for Backend Session Cookies.
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    from sqlalchemy.exc import IntegrityError
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="Server misconfigured")

    try:
        # Verify the token
        id_info = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            auth_req.id_token,
            google_requests.Request(),
            client_id
        )
        
        email = id_info['email']
        name = id_info.get('name')
        picture = id_info.get('picture')
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token")
    except Exception as e:
        logger.error(f"Google Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

    # Check or Create User
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if not user:
        try:
            user = User(
                email=email,
                full_name=name,
                avatar_url=picture,
                provider="google"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            await session.rollback()
            # Race condition hit - user created by another request in parallel
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=500, detail="Login failed")
        
    _set_auth_cookies(response, user.email)
    return {"message": "Google Login successful", "user": {"email": user.email, "full_name": user.full_name}}

@app.post("/api/auth/logout")
async def logout(response: Response):
    """Logout by clearing cookies."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}

@app.get("/api/auth/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return user

@app.delete("/api/auth/account")
async def delete_account(
    response: Response,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Permanently delete the authenticated user and all their data."""
    # Delete itineraries first (FK constraint)
    statement = select(Itinerary).where(Itinerary.user_id == user.id)
    result = await session.execute(statement)
    for itinerary in result.scalars().all():
        await session.delete(itinerary)
    # Delete user
    await session.delete(user)
    await session.commit()
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Account deleted"}

@app.get("/api/health")
async def health_check():
    return {"status": "online", "manager": "AntigravityAgentManager"}

@app.post("/api/chat", response_model=AgentResponse)
@limiter.limit("5/minute")
async def chat_endpoint(
    request: Request,
    chat_req: ChatRequest,
    user: Optional[User] = Depends(get_optional_user)
):
    """
    Main chat endpoint. Works for guests and authenticated users.
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

@app.post("/api/itinerary/save")
async def save_itinerary(
    save_req: SaveItineraryRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Save a generated itinerary. Requires authentication."""
    itinerary = Itinerary(
        user_id=user.id,
        destination=save_req.destination,
        summary=save_req.summary,
        data=save_req.itinerary_data,
        creative_assets=save_req.creative_assets
    )
    session.add(itinerary)
    await session.commit()
    await session.refresh(itinerary)
    return {"message": "Itinerary saved", "id": itinerary.id}

@app.post("/api/upload")
@limiter.limit("5/minute")
async def upload_file(request: Request, file: UploadFile = File(...)):
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
