# API Keys Guide

This document explains what API keys the Just Travel app uses, how to obtain them, and what happens if they're missing.

---

## 🔴 **REQUIRED** (App won't work without it)

### Google Gemini API Key
- **Variable:** `GOOGLE_API_KEY`
- **Purpose:** Powers all 6 AI agents (Profiler, Pathfinder, TrendSpotter, Concierge, Optimizer, CreativeDirector)
- **Includes:** Built-in Google Search grounding (web search with citations, no extra API key needed)
- **Get it at:** [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Without it:** The app cannot generate itineraries (all agents fail)
- **Billing:** Charged per search query that the model executes (as of Jan 2026)

---

## 🟡 **OPTIONAL** (Graceful mock fallback)

### OpenWeatherMap API Key
- **Variable:** `OPENWEATHERMAP_API_KEY`
- **Purpose:** 5-day weather forecast for destinations
- **Get it at:** [https://openweathermap.org/api](https://openweathermap.org/api)
- **Free tier:** 1,000 calls/day
- **Without it:** Uses deterministic hash-based mock weather data (still works, but not real-time)

### Google Maps/Places API Key
- **Variable:** `GOOGLE_MAPS_API_KEY`
- **Purpose:** Place search, geocoding, directions
- **Get it at:** [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
- **Enable:** Places API, Geocoding API, Directions API
- **Free tier:** $200 credit/month
- **Without it:** Returns sample mock places

### Neo4j Graph Database
- **Variables:** `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- **Purpose:** Destination discovery, connected locations
- **Get it at:** [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/)
- **Free tier:** AuraDB Free (persistent DB)
- **Without it:** Returns sample destinations from mock data

### Apify API Token
- **Variable:** `APIFY_API_TOKEN`
- **Purpose:** Social media trend analysis (Instagram, TikTok hashtags)
- **Get it at:** [https://console.apify.com/account/integrations](https://console.apify.com/account/integrations)
- **Free tier:** $5 credit/month
- **Without it:** Returns sample trending hashtags

### Amadeus Flight API
- **Variables:** `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET`
- **Purpose:** Real-time flight search
- **Get it at:** [https://developers.amadeus.com/](https://developers.amadeus.com/)
- **Free tier:** 2,000 API calls/month
- **Without it:** Returns sample flight data

### RapidAPI (Booking.com)
- **Variable:** `RAPIDAPI_KEY`
- **Purpose:** Hotel search
- **Get it at:** [https://rapidapi.com/DataCrawler/api/booking-com15](https://rapidapi.com/DataCrawler/api/booking-com15)
- **Free tier:** 500 requests/month
- **Without it:** Returns sample hotel listings

---

## 🔐 **AUTHENTICATION**

### NextAuth Secret
- **Variable:** `NEXTAUTH_SECRET`
- **Purpose:** Signs JWT tokens (access + refresh)
- **Generate with:** `openssl rand -base64 32`
- **Without it:** Uses a hardcoded fallback (OK for dev, **set it in production**)

### Google OAuth (Sign In with Google)
- **Variables:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Purpose:** Enables "Sign in with Google" button
- **Get it at:** [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
- **Setup:**
  1. Create OAuth 2.0 Client ID
  2. Set redirect URI: `http://localhost:3000/api/auth/callback/google`
- **Without it:** Users can still register/login with email+password

---

## 📝 **Quick Setup**

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. At minimum, add your **Google Gemini API key**:
   ```env
   GOOGLE_API_KEY=your_actual_key_here
   ```

3. (Optional) Add other keys as needed. The app will work with mock data for any missing keys.

4. Start the backend:
   ```bash
   cd just-travel-app
   uvicorn main:app --reload
   ```

---

## 🧪 **Testing Without Real APIs**

All tool classes have **deterministic mock fallbacks**:
- `WeatherTools` → Hash-based weather (same city = same forecast)
- `SearchTools` → Query-aware templates
- `MapsTools` → Sample places
- `CypherTools` → Sample destinations
- `SocialTools` → Sample hashtags
- `BookingTools` → Sample hotels
- `TransportTools` → Sample flights

This means you can run the full app with **only the Gemini API key** and still get realistic-looking itineraries.
