# Project Status & Architecture Overview

## 📍 Where We Are (Phase 2 Status)
We are currently **mid-way through Phase 2: Core Logic & Orchestration**.

| Component | Status | Description |
| :--- | :--- | :--- |
| **Foundation** | ✅ Complete | Next.js frontend, Python structure, and Neo-brutalist theme are ready. |
| **Backend API** | ✅ Complete | `main.py` is now a robust FastAPI server with an **Agent Manager** and **Rate Limiting**. |
| **Tools** | ✅ Complete | `cypher_tools`, `maps_tools`, and `social_tools` are implemented with **Mock Data Fallbacks**. |
| **Agent Logic** | 🚧 In Progress | Agents (`profiler`, `pathfinder`, etc.) exist but are not yet calling the real `tools` we just built. |
| **Integration** | 🚧 In Progress | Frontend is not yet talking to the Backend API. |

## 🏗️ Architecture Explanation

### 1. The Orchestrator (`main.py`)
This is the brain of the operation. Instead of a simple script, it's now an **Agent Manager** that enforces a specific workflow:
1.  **Input**: Receives user chat + context.
2.  **Sequential Step**: Calls `Profiler` to understand the user (Dietary, Budget, Interest).
3.  **Parallel Step**: If the intent is clear (e.g., "Plan a trip to Paris"), it triggers three agents simultaneously:
    *   **Pathfinder**: Queries Neo4j for known locations.
    *   **Trend Spotter**: Checks Apify (mock/real) for social trends.
    *   **Concierge**: Checks Google Maps (mock/real) for food/hotels.
4.  **Synthesis**: Uses `Optimizer` to bundle all results into a coherent response.

### 2. The Tools (`/tools`) & Resilience
We have built "resilient tools" that allow development to continue even if API keys are missing.

*   **MapsTools (`tools/maps_tools.py`)**: You mentioned a Google Maps API issue. **This is handled.** The code checks for a valid key. If missing or invalid, it gracefully falls back to generating **mock places** (e.g., "Sample Café", "Main Street"). This allows you to test the *flow* and *UI* without blocking on API access.
*   **SocialTools (`tools/social_tools.py`)**: Similarly, if Apify keys are missing, it generates fake "Trending Instagram Posts" so the UI has something to show.
*   **CypherTools (`tools/cypher_tools.py`)**: Connects to your Neo4j Aura instance. If connectivity fails, it returns mock graph data.

### 3. The Frontend (`/frontend`)
Currently, the frontend sends messages to a `simulateBackendResponse` function. The next big step is to switch this to `fetch('/api/chat')` so it talks to our real Python backend.

## 🚀 Next Steps
1.  **Wire Agents to Tools**: Modify `agents/pathfinder.py`, etc., to actually import and use the classes from `tools/`.
2.  **Connect Frontend**: Update `frontend/app/page.tsx` to hit `http://localhost:8000/api/chat`.
3.  **Run It**: Start both servers and verify the full loop.
