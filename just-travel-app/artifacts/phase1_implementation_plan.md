# Phase 1: Foundation & "Vibe Coding" Implementation Plan

## Goal
Initialize the "Just Travel" application with the requested hybrid architecture: Python ADK for agents and Next.js for the frontend.

## User Review Required
> [!IMPORTANT]
> You will need API keys for **Google Gemini**, **Neo4j** (Aura or local), **Apify**, and **Google Maps**. I will create a `.env` file in the root with placeholders.

## Proposed Changes

### Project Structure
Directory: `/home/a_y_o/Traveling App Hackaton/just-travel-app` (New Directory)

### Backend (Python ADK) [NEW]
- **Entry Point**: `main.py` (ADK Runner & Root Agent)
- **Dependencies**: `requirements.txt` (google-adk, neo4j, apify-client)
- **Agents**: `/agents` directory
    - `profiler.py`
    - `pathfinder.py`
    - `trend_spotter.py`
    - `concierge.py`
    - `optimizer.py`
- **Tools**: `/tools` directory
    - `cypher_tools.py`
    - `social_tools.py`
    - `maps_tools.py`

### Frontend (Next.js) [NEW]
- **Location**: `/frontend`
- **Framework**: Next.js (App Router)
- **Styling**: Tailwind CSS (Neo-brutalist theme)
- **Integration**: Will communicate with the basic ADK backend.

### Configuration [NEW]
- **.env**: Root level environment variables.

## Verification Plan
### Automated Tests
- Verify Python dependencies install: `pip install -r requirements.txt`
- Verify Next.js build: `cd frontend && npm run build`

### Manual Verification
- Check file structure matches user request exactly.
- Ensure `.env` exists with correct placeholders.
