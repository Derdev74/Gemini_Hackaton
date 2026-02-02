"""
Optimizer Agent
===============

This agent uses Gemini 3 to synthesize all research data into a coherent,
story-driven daily itinerary. It acts as the final composer.
"""

import logging
import json
import math
from typing import Optional
from datetime import datetime, timedelta
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class OptimizerAgent(BaseAgent):
    """
    Agent responsible for creating the final itinerary using LLM synthesis.
    """

    def __init__(self):
        super().__init__(name="optimizer", description="Synthesizes final itinerary using LLM", model_type="pro")
        logger.info("OptimizerAgent initialized with LLM")

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
        
        # Default start date if missing
        start_date_str = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
        You are the Master Travel Planner. Create a detailed, logical itinerary.
        
        User Query: "{query}"
        Profile: {json.dumps(profile, default=str)}
        
        Research Data:
        - Top Destinations Found: {self._summarize_list(destinations, 'name')}
        - Accommodations/Restaurants: {self._summarize_list(accommodations, 'name')}
        - Viral Trends: {self._summarize_list(trends, 'title')}
        
        Constraints:
        - Create a valid daily schedule.
        - Respect opening times if known (or assume standard 9am-5pm for museums, evening for dinner).
        - Group locations logically by geography to minimize travel time.
        - Include "estimated_cost" and "total_travel_time" estimates.
        
        Output JSON Schema ONLY:
        {{
            "summary": "Brief exciting narrative summary of the trip",
            "daily_itinerary": [
                {{
                    "day_number": 1,
                    "date": "YYYY-MM-DD",
                    "theme": "Culture & Food",
                    "estimated_cost": 150,
                    "time_slots": [
                        {{
                            "start_time": "09:00",
                            "end_time": "11:00",
                            "activity_type": "attraction",
                            "activity": {{ "name": "Louvre Museum", ... }},
                            "location": "Paris",
                            "notes": "Buy tickets in advance."
                        }}
                    ]
                }}
            ]
        }}
        """
        
        response_text = await self.generate_response(prompt, context=context)
        
        final_plan = {}
        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            final_plan = json.loads(clean_text)
            
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
        except:
            return "Data available"

    def _patch_dates(self, plan: dict, start_date_str: str):
        """Ensure dates are sequential starting from start_date."""
        try:
            current = datetime.strptime(start_date_str, "%Y-%m-%d")
            for day in plan.get("daily_itinerary", []):
                day["date"] = current.strftime("%Y-%m-%d")
                current += timedelta(days=1)
        except:
            pass
