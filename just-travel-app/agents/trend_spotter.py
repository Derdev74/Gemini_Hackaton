"""
Trend Spotter Agent
===================

This agent manages social media trend analysis using Apify actors.
It scrapes and analyzes trending content from platforms like
Instagram, TikTok, and travel blogs to identify popular destinations
and hidden gems.

The TrendSpotter helps users discover:
- Viral travel destinations
- Hidden gems mentioned by locals
- Seasonal trending locations
- Popular experiences and activities

Example Usage:
    trend_spotter = TrendSpotterAgent()
    trends = trend_spotter.process("What's trending in Bali?", {})
"""

import logging
from typing import Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.social_tools import SocialTools

logger = logging.getLogger(__name__)


class TrendSpotterAgent:
    """
    Agent responsible for social media trend analysis and discovery.

    The TrendSpotter uses Apify actors to scrape social media platforms
    and analyze trending travel content, providing users with up-to-date
    recommendations based on social popularity.

    Attributes:
        name: Agent identifier
        description: Brief description of agent capabilities
        social_tools: Instance of SocialTools for Apify operations
    """

    # Supported platforms and their keywords
    PLATFORM_KEYWORDS = {
        "instagram": ["instagram", "insta", "ig", "reels"],
        "tiktok": ["tiktok", "tik tok", "viral video"],
        "youtube": ["youtube", "vlog", "travel vlog"],
        "twitter": ["twitter", "x", "tweets"],
        "pinterest": ["pinterest", "pins"]
    }

    # Trend type classifications
    TREND_TYPES = {
        "viral": ["viral", "trending", "famous", "popular", "must-see"],
        "hidden_gem": ["hidden gem", "secret", "local favorite", "off the beaten path", "undiscovered"],
        "seasonal": ["seasonal", "best time", "when to visit", "peak season", "off-season"],
        "experience": ["experience", "activity", "things to do", "adventure", "tour"]
    }

    def __init__(self):
        """Initialize the Trend Spotter Agent."""
        self.name = "trend_spotter"
        self.description = "Analyzes social media trends for travel destinations"
        self.social_tools = SocialTools()
        self._trend_cache = {}  # Simple cache for recent trend data
        logger.info("TrendSpotterAgent initialized")

    def process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process a trend analysis query.

        Args:
            query: User's query about travel trends
            context: Optional context with destination info

        Returns:
            dict: Trend analysis results
        """
        context = context or {}
        query_lower = query.lower()

        # Determine which platforms to analyze
        platforms = self._detect_platforms(query_lower)

        # Determine the trend type being requested
        trend_type = self._detect_trend_type(query_lower)

        # Extract destination/location from query or context
        destination = self._extract_destination(query_lower, context)

        # Analyze trends
        if destination:
            trends = self._analyze_destination_trends(destination, platforms, trend_type)
        else:
            trends = self._get_general_travel_trends(platforms, trend_type)

        response = {
            "agent": self.name,
            "destination": destination,
            "platforms_analyzed": platforms,
            "trend_type": trend_type,
            "trends": trends,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if trends else "no_trends_found"
        }

        logger.info(f"TrendSpotter analyzed {len(trends)} trends for {destination or 'general travel'}")
        return response

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Async version of process for use in orchestrated workflows.

        Args:
            query: User's trend query
            context: Optional context dictionary

        Returns:
            dict: Trend analysis results
        """
        return self.process(query, context)

    def _detect_platforms(self, query: str) -> list:
        """
        Detect which social platforms to analyze.

        Args:
            query: User's query string

        Returns:
            list: Platforms to analyze
        """
        detected = []
        for platform, keywords in self.PLATFORM_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                detected.append(platform)

        # Default to all major platforms if none specified
        if not detected:
            detected = ["instagram", "tiktok"]

        return detected

    def _detect_trend_type(self, query: str) -> str:
        """
        Detect the type of trend being requested.

        Args:
            query: User's query string

        Returns:
            str: Trend type category
        """
        for trend_type, keywords in self.TREND_TYPES.items():
            if any(keyword in query for keyword in keywords):
                return trend_type

        return "viral"  # Default to viral/trending

    def _extract_destination(self, query: str, context: dict) -> Optional[str]:
        """
        Extract destination from query or context.

        Args:
            query: User's query string
            context: Session context

        Returns:
            Optional[str]: Extracted destination name
        """
        # Check context first
        destinations = context.get("destinations", {})
        if isinstance(destinations, dict) and destinations.get("results"):
            first_dest = destinations["results"][0]
            if isinstance(first_dest, dict):
                return first_dest.get("name")

        # Extract from query using common patterns
        location_indicators = [
            "in ", "for ", "about ", "trends in ", "trending in ",
            "popular in ", "visiting "
        ]

        for indicator in location_indicators:
            if indicator in query:
                idx = query.find(indicator) + len(indicator)
                remaining = query[idx:].strip()
                # Take first meaningful word(s)
                destination = remaining.split("?")[0].split(",")[0].strip()
                if destination and len(destination) > 1:
                    return destination.title()

        return None

    def _analyze_destination_trends(
        self,
        destination: str,
        platforms: list,
        trend_type: str
    ) -> list:
        """
        Analyze trends for a specific destination.

        Args:
            destination: Name of the destination
            platforms: List of platforms to analyze
            trend_type: Type of trends to find

        Returns:
            list: Trend data for the destination
        """
        trends = []

        # Search for destination-specific content
        search_queries = self._build_search_queries(destination, trend_type)

        for platform in platforms:
            platform_trends = self.social_tools.search_platform(
                platform=platform,
                queries=search_queries,
                limit=10
            )
            trends.extend(platform_trends)

        # Analyze and rank the trends
        analyzed_trends = self._analyze_and_rank(trends, trend_type)

        return analyzed_trends

    def _get_general_travel_trends(self, platforms: list, trend_type: str) -> list:
        """
        Get general travel trends across platforms.

        Args:
            platforms: List of platforms to analyze
            trend_type: Type of trends to find

        Returns:
            list: General travel trends
        """
        trends = []

        general_queries = [
            "travel 2024",
            "best destinations",
            "travel bucket list",
            "where to travel"
        ]

        for platform in platforms:
            platform_trends = self.social_tools.get_trending_content(
                platform=platform,
                category="travel",
                limit=10
            )
            trends.extend(platform_trends)

        return self._analyze_and_rank(trends, trend_type)

    def _build_search_queries(self, destination: str, trend_type: str) -> list:
        """
        Build search queries for a destination and trend type.

        Args:
            destination: Target destination
            trend_type: Type of trends

        Returns:
            list: Search query strings
        """
        queries = [
            f"{destination} travel",
            f"{destination} things to do",
            f"visit {destination}",
            f"{destination} guide"
        ]

        if trend_type == "hidden_gem":
            queries.extend([
                f"{destination} hidden gems",
                f"{destination} local spots",
                f"{destination} secret places"
            ])
        elif trend_type == "viral":
            queries.extend([
                f"{destination} viral",
                f"{destination} trending",
                f"{destination} must visit"
            ])
        elif trend_type == "experience":
            queries.extend([
                f"{destination} experiences",
                f"{destination} activities",
                f"{destination} tours"
            ])

        return queries

    def _analyze_and_rank(self, trends: list, trend_type: str) -> list:
        """
        Analyze and rank trends by relevance and engagement.

        Args:
            trends: Raw trend data
            trend_type: Type of trends for scoring

        Returns:
            list: Ranked and analyzed trends
        """
        analyzed = []

        for trend in trends:
            # Calculate trend score based on engagement metrics
            score = self._calculate_trend_score(trend, trend_type)

            analyzed_trend = {
                "title": trend.get("title", ""),
                "description": trend.get("description", ""),
                "platform": trend.get("platform", "unknown"),
                "engagement": trend.get("engagement", {}),
                "url": trend.get("url", ""),
                "trend_score": score,
                "trend_type": trend_type,
                "extracted_locations": trend.get("locations", []),
                "hashtags": trend.get("hashtags", [])
            }
            analyzed.append(analyzed_trend)

        # Sort by trend score (descending)
        analyzed.sort(key=lambda x: x["trend_score"], reverse=True)

        return analyzed[:20]  # Return top 20 trends

    def _calculate_trend_score(self, trend: dict, trend_type: str) -> float:
        """
        Calculate a relevance score for a trend.

        Args:
            trend: Trend data dictionary
            trend_type: Type of trend for weighting

        Returns:
            float: Trend score (0-100)
        """
        engagement = trend.get("engagement", {})

        # Base score from engagement metrics
        likes = engagement.get("likes", 0)
        comments = engagement.get("comments", 0)
        shares = engagement.get("shares", 0)
        views = engagement.get("views", 0)

        # Normalize and weight engagement
        base_score = (
            (min(likes, 100000) / 1000) +
            (min(comments, 10000) / 100) +
            (min(shares, 50000) / 500) +
            (min(views, 1000000) / 10000)
        )

        # Apply trend type multiplier
        type_multipliers = {
            "viral": 1.2,
            "hidden_gem": 0.8,  # Hidden gems have lower engagement by nature
            "seasonal": 1.0,
            "experience": 1.1
        }
        multiplier = type_multipliers.get(trend_type, 1.0)

        # Recency boost (newer content scores higher)
        # This would use actual timestamps in production
        recency_boost = 1.0

        final_score = min(base_score * multiplier * recency_boost, 100)
        return round(final_score, 2)

    def get_trending_hashtags(self, destination: str, platform: str = "instagram") -> list:
        """
        Get trending hashtags for a destination.

        Args:
            destination: Target destination
            platform: Social platform

        Returns:
            list: Trending hashtags
        """
        return self.social_tools.get_trending_hashtags(
            destination=destination,
            platform=platform,
            limit=20
        )

    def get_influencer_recommendations(self, destination: str) -> list:
        """
        Get travel influencer recommendations for a destination.

        Args:
            destination: Target destination

        Returns:
            list: Influencer recommendation posts
        """
        return self.social_tools.search_influencer_content(
            destination=destination,
            min_followers=10000,
            limit=10
        )
