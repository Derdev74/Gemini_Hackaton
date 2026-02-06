# Phase 2: Core Logic & Agent Orchestration Implementation Plan

## Goal
Transition from the static "Vibe Coding" foundation to a functional dynamic application. This involves "API-ifying" the Python backend, connecting the frontend to it, and implementing the core logic for the "Boxes" (Routing, Concierge, Hidden Gems).

## User Review Required
> [!IMPORTANT]
> This phase requires your **Neo4j** database to be running and accessible for the Pathfinder agent to work.
> Ensure your `just-travel-app/.env` file is populated with your API keys.

## Proposed Changes

### Backend (Python ADK)
#### 1. API Server Implementation (`main.py`)
- **Action**: Refactor `main.py` to expose a FastAPI application.
- **Rate Limiting**: Integration of `slowapi` to limit API calls (e.g., 5 requests/minute per IP) to prevent abuse and manage API costs.
- **Endpoints**:
    - `POST /api/chat`: Main entry point for user queries.
    - `GET /api/health`: Health check.

#### 2. Deterministic Agentic Workflow (Google ADK)
- **Goal**: Replace ad-hoc routing with a structured, deterministic workflow using ADK primitives.
- **Workflow Definition**:
    1.  **Profiler Agent** (Sequential): Analyzes user input to update the state (Preferences).
    2.  **Research Phase** (Parallel):
        - **Pathfinder**: Queries Neo4j for destinations matching the profile.
        - **Trend Spotter**: Checks Apify for social trends.
        - **Concierge**: Checks Google Maps/Places for venues.
    3.  **Optimizer Agent** (Sequential): Synthesizes all data into a final Itinerary.
- **Implementation**: Use a coordinator pattern in `main.py` to enforce this `Sequential -> Parallel -> Sequential` flow.

#### 3. Tool Implementation (`/tools`)
- **`cypher_tools.py`**: Verify connection logic and ensure queries work with standard Neo4j schemas.
- **`maps_tools.py`**: [NEW] Implement Google Places API wrappers to find restaurants/hotels (Concierge).
- **`social_tools.py`**: [NEW] Implement Apify client wrappers to fetch trends (Trend Spotter).

### Frontend (Next.js)
#### 1. API Integration (`app/page.tsx`)
- **Action**: Replace `simulateBackendResponse` with `fetch('http://localhost:8000/api/chat', ...)`.
- **State Handling**: Update the usage of the returned JSON to update the `preferences` and `itinerary` state.

#### 2. Itinerary Visualization (`components/ItineraryView.tsx`)
- **Action**: Create a new component to render the "Dynamic Daily Planner" (Box 6) when the backend returns a generated itinerary.
- **Style**: Apply the Neo-brutalist cards to this view.

## Verification Plan

### Automated Tests
- **Backend**: Create a test script `test_api.py` to hit the `/api/chat` endpoint and verify JSON structure.
- **Tools**: Run individual tool scripts to verify API connectivity (e.g., `python tools/maps_tools.py`).

### Manual Verification
1.  Start Backend: `uvicorn main:app --reload`
2.  Start Frontend: `npm run dev`
3.  **User Flow**:
    - Type "I want a vegan trip to Tokyo".
    - Verify Frontend sends request to Backend.
    - Verify Backend (Profiler) extracts "vegan" and "Tokyo".
    - Verify Backend (Pathfinder) queries Neo4j (or mock).
    - Verify Frontend displays the response from the Agent.
