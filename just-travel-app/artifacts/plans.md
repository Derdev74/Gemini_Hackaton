# Just Travel - Implementation Plans

> This file contains verifiable implementation plans created by the AI agents.
> Auto-generated documentation for travel planning sessions.

---

## Phase 1: Foundation Complete

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Just Travel Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Frontend (Next.js)                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │   Chat UI   │  │  Features   │  │   Itinerary     │   │  │
│  │  │  Interface  │  │   Display   │  │    Display      │   │  │
│  │  └──────┬──────┘  └─────────────┘  └─────────────────┘   │  │
│  └─────────┼────────────────────────────────────────────────┘  │
│            │                                                     │
│            │ HTTP/WebSocket                                      │
│            ▼                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 Backend (Python ADK)                       │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              Root Agent (main.py)                    │  │  │
│  │  │         Orchestrates all specialist agents           │  │  │
│  │  └─────────────────────┬──────────────────────────────┘  │  │
│  │                        │                                   │  │
│  │    ┌───────────────────┼───────────────────┐             │  │
│  │    ▼                   ▼                   ▼              │  │
│  │ ┌──────────┐    ┌──────────┐    ┌──────────────┐        │  │
│  │ │ Profiler │    │Pathfinder│    │ TrendSpotter │        │  │
│  │ │  Agent   │    │  Agent   │    │    Agent     │        │  │
│  │ └──────────┘    └──────────┘    └──────────────┘        │  │
│  │                        │                                   │  │
│  │    ┌───────────────────┼───────────────────┐             │  │
│  │    ▼                   ▼                                  │  │
│  │ ┌──────────┐    ┌──────────┐                             │  │
│  │ │Concierge │    │Optimizer │                             │  │
│  │ │  Agent   │    │  Agent   │                             │  │
│  │ └──────────┘    └──────────┘                             │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                        │                                         │
│    ┌───────────────────┼───────────────────┐                    │
│    ▼                   ▼                   ▼                    │
│ ┌──────────┐    ┌──────────┐    ┌──────────────┐              │
│ │  Neo4j   │    │  Apify   │    │ Google Maps  │              │
│ │  Graph   │    │  Social  │    │   Places     │              │
│ │   DB     │    │ Scraping │    │     API      │              │
│ └──────────┘    └──────────┘    └──────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### 1. Profiler Agent
**Purpose**: Capture user preferences and constraints

**Capabilities**:
- Extract dietary restrictions (vegetarian, vegan, halal, kosher)
- Identify religious requirements
- Determine budget level (budget, moderate, luxury)
- Capture travel style preferences
- Track group size and accessibility needs

**Input**: Natural language user messages
**Output**: Structured TravelerProfile object

---

### 2. Pathfinder Agent
**Purpose**: Graph-based destination discovery

**Capabilities**:
- Query Neo4j for destinations by category
- Find nearby attractions
- Discover connected destinations
- Calculate optimal routes
- Search by region/location

**Tools Used**: CypherTools (Neo4j)

---

### 3. TrendSpotter Agent
**Purpose**: Social media trend analysis

**Capabilities**:
- Scrape Instagram for travel content
- Analyze TikTok travel trends
- Identify viral destinations
- Discover hidden gems
- Track trending hashtags

**Tools Used**: SocialTools (Apify)

---

### 4. Concierge Agent
**Purpose**: Accommodation and dining recommendations

**Capabilities**:
- Search hotels matching budget
- Find restaurants with dietary options
- Filter by ratings and reviews
- Verify opening hours
- Check accessibility features

**Tools Used**: MapsTools (Google Places)

---

### 5. Optimizer Agent
**Purpose**: Itinerary optimization

**Capabilities**:
- Create day-by-day schedules
- Optimize travel between locations
- Allocate time for activities
- Include meal planning
- Add buffer and rest time

**Output**: Complete DayPlan objects with TimeSlots

---

## API Keys Required

| Service | Environment Variable | Purpose |
|---------|---------------------|---------|
| Google Gemini | `GOOGLE_API_KEY` | AI/LLM capabilities |
| Neo4j | `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` | Graph database |
| Apify | `APIFY_API_TOKEN` | Social media scraping |
| Google Maps | `GOOGLE_MAPS_API_KEY` | Places and Maps API |

---

## Phase 2 Roadmap

1. **Real API Integration**: Connect all tools to live APIs
2. **WebSocket Support**: Real-time chat communication
3. **User Authentication**: Save preferences and trip history
4. **Booking Integration**: Connect to booking platforms
5. **Mobile App**: React Native or Flutter version

---

## Development Notes

### Running the Backend
```bash
cd just-travel-app
pip install -r requirements.txt
python main.py
```

### Running the Frontend
```bash
cd just-travel-app/frontend
npm install
npm run dev
```

### Testing
- Backend tests: `pytest tests/`
- Frontend tests: `npm run test`

---

*Last updated: Phase 1 Foundation*
