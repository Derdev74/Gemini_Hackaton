"""
Trend Spotter Agent
===================

This agent uses Gemini 3 to synthesize social media trends from Apify data.
It extracts 'vibes' and trending locations from raw social data.
"""

import logging
import json
import sys
import os
from typing import Optional
from agents.base import BaseAgent

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.social_tools import SocialTools

logger = logging.getLogger(__name__)

class TrendSpotterAgent(BaseAgent):
    """
    Agent responsible for identifying travel trends using LLM + Social Data.
    """

    def __init__(self):
        super().__init__(name="trend_spotter", description="Analyzes trends using LLM", model_type="flash")
        self.social_tools = SocialTools()
        logger.info("TrendSpotterAgent initialized with LLM")

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Fetch social data and use LLM to synthesize a 'Trend Report'.
        """
        context = context or {}
        location = context.get("destination", "Global")
        
        # 1. Fetch Raw Data (Using Mock/Real Tools)
        # We start with a broad search based on the query
        raw_trends = self.social_tools.get_trending_hashtags(location)
        formatted_posts = self.social_tools.search_travel_content(location)
        
        # 2. LLM Synthesis
        prompt = f"""
        You are a cool travel trend spotter.
        Location: {location}
        
        Social Media Data:
        {json.dumps(formatted_posts[:10], default=str)}
        
        Trending Hashtags:
        {raw_trends}
        
        Task:
        1. Identify the top 3 specific activities or locations that are "viral" right now.
        2. Give each a "Vibe Score" (1-100).
        3. Explain *why* it's trending (e.g., "Featured in Emily in Paris", "TikTok sunset spot").
        
        Output JSON ONLY:
        {{
            "trends": [
                {{
                    "title": "Name of activity/place",
                    "trend_score": 95,
                    "description": "Why it is cool...",
                    "extracted_locations": ["Location Name"]
                }}
            ],
            "overall_vibe": "Chill", 
            "keywords": ["aesthetic", "coffee"]
        }}
        """
        
        response_text = await self.generate_response(prompt, context=context)
        
        final_trends = []
        
        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            final_trends = data.get("trends", [])
        except Exception as e:
            logger.error(f"TrendSpotter synthesis error: {e}")
            
        return {
            "agent": self.name,
            "trends": final_trends,
            "raw_count": len(formatted_posts),
            "status": "success"
        }
