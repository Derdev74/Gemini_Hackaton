"""
Optimizer Agent
===============

This agent uses Gemini 3 to synthesize all research data into a coherent,
story-driven daily itinerary. It acts as the final composer.
"""

import logging
import json
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from agents.base import BaseAgent
from tools.weather_tools import WeatherTools

logger = logging.getLogger(__name__)

class OptimizerAgent(BaseAgent):
    """
    Agent responsible for creating the final itinerary using LLM synthesis.
    """

    def __init__(self):
        super().__init__(name="optimizer", description="Synthesizes final itinerary using LLM", model_type="pro")
        self.weather_tools = WeatherTools()
        logger.info("OptimizerAgent initialized with LLM + WeatherTools")

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Synthesize inputs from all agents into a final JSON itinerary.
        """
        context = context or {}
        
        # Gather inputs
        profile = context.get("profile", {})
        destinations = context.get("destinations", [])
        accommodations = context.get("accommodations", [])
        trends = context.get("trends", [])

        # Extract Amadeus intelligence if Pathfinder provided it
        amadeus_intel = None
        if isinstance(destinations, dict) and "amadeus_intelligence" in destinations:
            amadeus_intel = destinations.get("amadeus_intelligence")
        elif isinstance(destinations, list):
            for dest in destinations:
                if isinstance(dest, dict) and "amadeus_intelligence" in dest:
                    amadeus_intel = dest.get("amadeus_intelligence")
                    break

        # Default start date if missing
        start_date_str = datetime.now().strftime("%Y-%m-%d")

        # Resolve destination city for weather lookup
        dest_city = profile.get("destination") or ""
        if not dest_city and destinations:
            dest_city = destinations[0].get("name", "")

        # Fetch weather forecast (non-blocking)
        weather_data = {}
        weather_section = ""
        if dest_city:
            try:
                weather_data = await asyncio.to_thread(
                    self.weather_tools.get_forecast, dest_city, 5
                )
                forecasts = weather_data.get("forecasts", [])
                if forecasts:
                    lines = []
                    for f in forecasts:
                        line = f"{f['date']}: {f['condition']}, {f['temp_min_c']}–{f['temp_max_c']}°C"
                        if f.get("advisory"):
                            line += f"  {f['advisory']}"
                        lines.append(line)
                    weather_section = "Weather Forecast:\n" + "\n".join(lines)
            except Exception as e:
                logger.warning(f"Weather fetch failed for '{dest_city}': {e}")

        prompt = f"""
        You are the Master Travel Planner. Create a COMPLETE trip plan from departure to return.

        User Query: "{query}"
        Profile: {json.dumps(profile, default=str)}

        Research Data (USE THIS TO BUILD THE PLAN):
        - Flights/Transport: {json.dumps(self._extract_flights(destinations), default=str)}
        - Accommodations: {json.dumps(accommodations[:5], default=str)}
        - Restaurants: {json.dumps(self._extract_restaurants(accommodations), default=str)}
        - Attractions: {self._summarize_list(destinations, 'name')}
        - Viral Trends: {self._summarize_list(trends, 'title')}

        {weather_section}

        {self._format_flight_intelligence(amadeus_intel)}

        REQUIREMENTS:
        1. Day 1 MUST start with arrival (flight landing, airport transfer, hotel check-in)
        2. Last day MUST end with departure (hotel checkout, airport transfer, flight)
        3. Each day includes: breakfast or brunch, activities, lunch, activities, dinner
        4. Include transport between all locations
        5. Group activities by geography to minimize travel time
        6. Respect weather forecast (no outdoor activities in rain/storms)
        7. Respect opening times (museums 9am-5pm, restaurants for meals)

        Output JSON Schema ONLY:
        {{
            "summary": "Exciting narrative of the journey",
            "trip_title": "Catchy title (e.g., '5 Days in Paris')",
            "trip_visual_theme": "Visual mood for poster (e.g., 'Romance in the City of Lights')",

            "flights": {{
                "outbound": {{
                    "airline": "Airline Name",
                    "flight_number": "XX123",
                    "departure_airport": "JFK",
                    "arrival_airport": "CDG",
                    "departure_time": "2026-02-08T18:00",
                    "arrival_time": "2026-02-09T07:30",
                    "price_estimate": 450
                }},
                "return": {{
                    "airline": "Airline Name",
                    "flight_number": "XX456",
                    "departure_airport": "CDG",
                    "arrival_airport": "JFK",
                    "departure_time": "2026-02-13T10:00",
                    "arrival_time": "2026-02-13T13:30",
                    "price_estimate": 420
                }}
            }},

            "accommodation": {{
                "name": "Hotel Name",
                "type": "hotel",
                "address": "Full address",
                "check_in": "2026-02-09",
                "check_out": "2026-02-13",
                "price_per_night": 180,
                "total_nights": 4,
                "notes": "Description"
            }},

            "daily_itinerary": [
                {{
                    "day_number": 1,
                    "date": "YYYY-MM-DD",
                    "theme": "Arrival & First Impressions",
                    "daily_highlight": "Most photogenic moment",
                    "visual_theme": "Mood for poster (e.g., 'Golden evening lights')",
                    "key_locations": ["Airport", "Hotel", "Main Attraction"],
                    "estimated_cost": 150,
                    "total_travel_time": 90,
                    "time_slots": [
                        {{
                            "start_time": "07:30",
                            "end_time": "09:00",
                            "activity_type": "arrival",
                            "activity": {{ "name": "Land at Airport", "type": "flight_arrival" }},
                            "location": "Airport Name",
                            "notes": "Collect luggage"
                        }},
                        {{
                            "start_time": "09:00",
                            "end_time": "10:00",
                            "activity_type": "transport",
                            "activity": {{ "name": "Airport Transfer", "type": "taxi", "price_level": 2 }},
                            "location": "Airport → Hotel",
                            "notes": "45 min by taxi"
                        }},
                        {{
                            "start_time": "10:00",
                            "end_time": "11:00",
                            "activity_type": "accommodation",
                            "activity": {{ "name": "Hotel Check-in", "type": "check_in" }},
                            "location": "Hotel Name",
                            "notes": "Drop luggage"
                        }},
                        {{
                            "start_time": "12:30",
                            "end_time": "14:00",
                            "activity_type": "meal",
                            "activity": {{ "name": "Restaurant Name", "type": "lunch", "cuisine": "Local", "price_level": 2 }},
                            "location": "Restaurant Address",
                            "notes": "Try the local specialty"
                        }},
                        {{
                            "start_time": "15:00",
                            "end_time": "18:00",
                            "activity_type": "attraction",
                            "activity": {{ "name": "Main Attraction", "type": "museum", "price_level": 2 }},
                            "location": "Attraction Address",
                            "notes": "Book tickets in advance"
                        }},
                        {{
                            "start_time": "19:30",
                            "end_time": "21:30",
                            "activity_type": "meal",
                            "activity": {{ "name": "Dinner Restaurant", "type": "dinner", "cuisine": "Local", "price_level": 3 }},
                            "location": "Restaurant Address",
                            "notes": "Reservation recommended"
                        }}
                    ]
                }}
            ]
        }}

        IMPORTANT: Last day must include checkout and departure activities.
        """
        
        response_text = await self.generate_response(prompt, context=context)
        
        final_plan = {}
        try:
            final_plan = self.parse_json_response(response_text)
            
            # Simple validation/patching of dates
            self._patch_dates(final_plan, start_date_str)
            
        except Exception as e:
            logger.error(f"Optimizer synthesis error: {e}")
            final_plan = {
                "summary": "We encountered an issue generating your detailed plan, but we have your preferences saved!",
                "daily_itinerary": []
            }

        return final_plan

    def _summarize_list(self, items: list, key: str) -> str:
        """Helper to create short summaries for the prompt context."""
        if not items:
            return "None"
        try:
            # Take top 10 to fit in context window
            names = [str(item.get(key, "Unknown")) for item in items[:10]]
            return ", ".join(names)
        except Exception as e:
            logger.warning(f"Failed to summarize list for key {key}: {e}")
            return "Data available"

    def _patch_dates(self, plan: dict, start_date_str: str):
        """Ensure dates are sequential starting from start_date."""
        try:
            current = datetime.strptime(start_date_str, "%Y-%m-%d")
            for day in plan.get("daily_itinerary", []):
                day["date"] = current.strftime("%Y-%m-%d")
                current += timedelta(days=1)
        except Exception:
            pass

    def _format_flight_intelligence(self, amadeus_intel: Optional[dict]) -> str:
        """
        Format Amadeus flight intelligence for prompt injection.

        This gives the LLM smart money-saving insights to include in suggestions.
        """
        if not amadeus_intel:
            return ""

        sections = []

        # Cheapest dates analysis
        cheapest = amadeus_intel.get("cheapest_dates", {})
        if cheapest and cheapest.get("cheapest_date"):
            savings = cheapest.get("savings_vs_target", 0)
            if savings and savings > 50:  # Only show if meaningful savings
                sections.append(
                    f"💰 FLIGHT SAVINGS OPPORTUNITY: Shifting dates to {cheapest['cheapest_date']} "
                    f"could save ${savings:.0f} on flights."
                )

        # Price confidence analysis
        analysis = amadeus_intel.get("price_analysis", {})
        if analysis and analysis.get("confidence"):
            confidence = analysis["confidence"]
            recommendation = analysis.get("recommendation", "")
            if confidence == "Great Deal":
                sections.append(
                    f"✅ FLIGHT DEAL ALERT: {recommendation}"
                )
            elif confidence == "High Price":
                sections.append(
                    f"⚠️  FLIGHT PRICING NOTE: {recommendation}"
                )

        if not sections:
            return ""

        return "Flight Intelligence (for your money-saving suggestions):\n" + "\n".join(sections)

    def _extract_flights(self, destinations) -> list:
        """Extract flight data from Pathfinder results."""
        flights = []
        if isinstance(destinations, dict):
            flights = destinations.get("flights", [])
        elif isinstance(destinations, list):
            for d in destinations:
                if isinstance(d, dict) and "flights" in d:
                    flights.extend(d.get("flights", []))
        return flights[:3]  # Top 3 flight options

    def _extract_restaurants(self, accommodations: list) -> list:
        """Extract restaurant recommendations from Concierge results."""
        restaurants = []
        for item in accommodations:
            if isinstance(item, dict):
                item_type = str(item.get("type", "")).lower()
                if "restaurant" in item_type or "cafe" in item_type or "dining" in item_type:
                    restaurants.append(item)
        return restaurants[:10]
