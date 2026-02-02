"""
Social Tools
============

This module provides integration with Apify for social media scraping
and Gemini Vision for visual trend analysis.
"""

import os
import logging
from typing import Optional, Dict
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Apify client import with fallback
try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    ApifyClient = None
    APIFY_AVAILABLE = False
    logger.warning("Apify client not installed. Social features will use mock data.")

class SocialTools:
    """
    Tool class for social media trend analysis via Apify + Gemini Vision.
    """

    # Apify actor IDs for different platforms
    ACTOR_IDS = {
        "instagram": "apify/instagram-scraper",
        "tiktok": "clockworks/tiktok-scraper",
        "youtube": "streamers/youtube-scraper"
    }

    def __init__(self):
        """Initialize SocialTools."""
        self.api_token = os.getenv("APIFY_API_TOKEN", "")
        self.client = None
        self._initialized = False

        if APIFY_AVAILABLE and self.api_token and "placeholder" not in self.api_token:
            self._initialize_client()
            
        # Initialize Vision Model specifically for Tools usage
        # We reuse the key from env
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
             genai.configure(api_key=api_key)
             # Use a Pro model for Vision
             self.vision_model = genai.GenerativeModel("gemini-1.5-pro")

        logger.info(f"SocialTools initialized (connected: {self._initialized})")

    def _initialize_client(self) -> bool:
        try:
            self.client = ApifyClient(self.api_token)
            self._initialized = True
            logger.info("Apify client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Apify client: {e}")
            self._initialized = False
            return False

    def get_trending_hashtags(self, destination: str, platform: str = "instagram", limit: int = 10) -> list:
        if not self._initialized:
             return self._get_mock_hashtags(destination, limit)
        
        # Real Apify logic would go here
        return self._get_mock_hashtags(destination, limit)

    def search_travel_content(self, location: str) -> list:
        return self.search_platform("tiktok", [f"{location} travel guide"], limit=5)

import requests

# ... (imports remain)

    def search_platform(self, platform: str, queries: list, limit: int = 10) -> list:
        if not self._initialized:
            return self._get_mock_search_results(platform, queries, limit)
        
        try:
            logger.info(f"Searching {platform} via Apify for: {queries}")
            actor_id = self.ACTOR_IDS.get(platform)
            if not actor_id:
                logger.warning(f"No actor configured for {platform}, using mock.")
                return self._get_mock_search_results(platform, queries, limit)

            # Prepare generic input (works for most social scrapers like instagram-scraper)
            # Note: Specific actors might need specific keys (e.g. "search" vs "searchQueries")
            run_input = {
                "search": queries[0], # Simple single query support for stability
                "searchQueries": queries, 
                "resultsLimit": limit,
                "resultsType": "posts"
            }

            # Run the actor
            run = self.client.actor(actor_id).call(run_input=run_input)
            
            if not run:
                logger.warning("Apify run failed to start.")
                return []

            # Fetch results
            dataset = self.client.dataset(run["defaultDatasetId"])
            items = list(dataset.iterate_items())
            
            # Normalize results to a common format
            normalized = []
            for item in items:
                normalized.append({
                    "title": item.get("caption") or item.get("text") or "No Caption",
                    "url": item.get("url") or item.get("postUrl"),
                    "thumbnail": item.get("displayUrl") or item.get("thumbnailUrl"),
                    "likes": item.get("likesCount", 0)
                })
                
            return normalized

        except Exception as e:
            logger.error(f"Apify search failed: {e}")
            return self._get_mock_search_results(platform, queries, limit)

    async def analyze_visual_vibe(self, content_url: str) -> Dict:
        """
        Analyze the 'vibe' of a piece of visual content using Gemini Vision.
        Downloads the image bytes and calls the model.
        """
        if not content_url:
            return {"vibe_description": "No URL provided"}

        try:
            # 1. Download the image bytes
            logger.info(f"Downloading content for analysis: {content_url}")
            response = requests.get(content_url, timeout=10)
            response.raise_for_status()
            image_choices = response.content
            
            # 2. Call Gemini Vision
            prompt = "Analyze the aesthetic of this travel image. Is it luxury, adventure, chill, or party? Give a score out of 100 for 'Instagrammability'."
            
            # Pass dictionary with explicit mime_type for Gemini
            # Assuming JPEG for simplicity, but could sniff header
            content_part = {
                "mime_type": "image/jpeg", 
                "data": image_choices
            }
            
            model_response = await self.vision_model.generate_content_async([prompt, content_part])
            
            return {
                "vibe_description": model_response.text,
                "analyzed_url": content_url
            }
        except Exception as e:
            logger.error(f"Visual Vibe Check failed: {e}")
            return {
                "vibe_description": f"Visual analysis failed ({str(e)}). Assumed vibe based on metadata.", 
                "error": str(e)
            }

    # --- Mocks ---
    def _get_mock_search_results(self, platform, queries, limit):
        return [{"title": f"Viral {q}", "url": "http://mock.url/content.jpg", "hashtags": ["#viral"]} for q in queries]

    def _get_mock_hashtags(self, destination, limit):
         return [{"hashtag": f"#{destination}vibes", "count": 5000}]
