"""
Social Tools
============

This module provides integration with Apify for social media scraping
and trend analysis across various platforms.

The SocialTools class handles:
- Apify actor management
- Social media content scraping
- Trend detection and analysis
- Hashtag and influencer discovery

Example Usage:
    tools = SocialTools()
    trends = tools.search_platform("instagram", ["bali travel"], limit=10)
"""

import os
import logging
from typing import Optional
from datetime import datetime

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
    Tool class for social media trend analysis via Apify.

    This class manages Apify actors for scraping and analyzing
    social media content to identify travel trends.

    Attributes:
        api_token: Apify API token
        client: Apify client instance
    """

    # Apify actor IDs for different platforms
    ACTOR_IDS = {
        "instagram": "apify/instagram-scraper",
        "tiktok": "clockworks/tiktok-scraper",
        "youtube": "streamers/youtube-scraper",
        "twitter": "quacker/twitter-scraper"
    }

    def __init__(self):
        """Initialize SocialTools with API token from environment."""
        self.api_token = os.getenv("APIFY_API_TOKEN", "")
        self.client = None
        self._initialized = False

        # Initialize client if available
        if APIFY_AVAILABLE and self.api_token and "your_" not in self.api_token:
            self._initialize_client()

        logger.info(f"SocialTools initialized (connected: {self._initialized})")

    def _initialize_client(self) -> bool:
        """
        Initialize the Apify client.

        Returns:
            bool: True if initialization successful
        """
        try:
            self.client = ApifyClient(self.api_token)
            self._initialized = True
            logger.info("Apify client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Apify client: {e}")
            self._initialized = False
            return False

    def search_platform(
        self,
        platform: str,
        queries: list,
        limit: int = 10
    ) -> list:
        """
        Search a social platform for travel content.

        Args:
            platform: Platform name (instagram, tiktok, etc.)
            queries: List of search queries
            limit: Maximum results per query

        Returns:
            list: Scraped content results
        """
        if not self._initialized:
            logger.warning(f"Apify not initialized, returning mock data for {platform}")
            return self._get_mock_search_results(platform, queries, limit)

        actor_id = self.ACTOR_IDS.get(platform)
        if not actor_id:
            logger.warning(f"Unknown platform: {platform}")
            return []

        all_results = []

        for query in queries:
            try:
                # Run the appropriate actor
                run_input = self._build_actor_input(platform, query, limit)
                run = self.client.actor(actor_id).call(run_input=run_input)

                # Get results from dataset
                dataset_items = self.client.dataset(run["defaultDatasetId"]).iterate_items()

                for item in dataset_items:
                    formatted = self._format_platform_result(platform, item, query)
                    all_results.append(formatted)

            except Exception as e:
                logger.error(f"Error scraping {platform} for '{query}': {e}")
                # Fall back to mock data for this query
                all_results.extend(self._get_mock_search_results(platform, [query], limit))

        return all_results[:limit * len(queries)]

    def get_trending_content(
        self,
        platform: str,
        category: str = "travel",
        limit: int = 10
    ) -> list:
        """
        Get trending content for a category.

        Args:
            platform: Platform name
            category: Content category
            limit: Maximum results

        Returns:
            list: Trending content
        """
        if not self._initialized:
            return self._get_mock_trending(platform, category, limit)

        # Build trending search queries
        trending_queries = [
            f"#{category}",
            f"#{category}2024",
            f"best {category}",
            f"{category} bucket list"
        ]

        return self.search_platform(platform, trending_queries, limit)

    def get_trending_hashtags(
        self,
        destination: str,
        platform: str = "instagram",
        limit: int = 20
    ) -> list:
        """
        Get trending hashtags for a destination.

        Args:
            destination: Destination name
            platform: Platform to search
            limit: Maximum hashtags

        Returns:
            list: Trending hashtags
        """
        if not self._initialized:
            return self._get_mock_hashtags(destination, limit)

        # Search for destination content and extract hashtags
        results = self.search_platform(platform, [destination], limit)

        hashtag_counts = {}
        for result in results:
            for hashtag in result.get("hashtags", []):
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

        # Sort by frequency
        sorted_hashtags = sorted(
            hashtag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"hashtag": tag, "count": count}
            for tag, count in sorted_hashtags[:limit]
        ]

    def search_influencer_content(
        self,
        destination: str,
        min_followers: int = 10000,
        limit: int = 10
    ) -> list:
        """
        Search for travel influencer content about a destination.

        Args:
            destination: Destination name
            min_followers: Minimum follower count
            limit: Maximum results

        Returns:
            list: Influencer content
        """
        if not self._initialized:
            return self._get_mock_influencer_content(destination, limit)

        # Search with influencer-focused queries
        queries = [
            f"{destination} travel blogger",
            f"{destination} travel influencer",
            f"{destination} travel guide"
        ]

        results = self.search_platform("instagram", queries, limit)

        # Filter by follower count
        filtered = [
            r for r in results
            if r.get("author_followers", 0) >= min_followers
        ]

        return filtered[:limit]

    def _build_actor_input(self, platform: str, query: str, limit: int) -> dict:
        """
        Build input configuration for Apify actor.

        Args:
            platform: Platform name
            query: Search query
            limit: Maximum results

        Returns:
            dict: Actor input configuration
        """
        base_input = {
            "resultsLimit": limit,
            "searchType": "hashtag"
        }

        if platform == "instagram":
            return {
                **base_input,
                "search": query,
                "resultsType": "posts"
            }
        elif platform == "tiktok":
            return {
                **base_input,
                "searchQueries": [query],
                "resultsPerPage": limit
            }
        elif platform == "youtube":
            return {
                "searchKeywords": query,
                "maxResults": limit
            }
        else:
            return {"query": query, "limit": limit}

    def _format_platform_result(self, platform: str, item: dict, query: str) -> dict:
        """
        Format raw platform result into standard format.

        Args:
            platform: Platform name
            item: Raw result item
            query: Original query

        Returns:
            dict: Formatted result
        """
        # Common format for all platforms
        formatted = {
            "platform": platform,
            "query": query,
            "title": "",
            "description": "",
            "url": "",
            "engagement": {},
            "hashtags": [],
            "locations": [],
            "author": "",
            "author_followers": 0,
            "timestamp": datetime.now().isoformat()
        }

        if platform == "instagram":
            formatted.update({
                "title": item.get("caption", "")[:100],
                "description": item.get("caption", ""),
                "url": item.get("url", ""),
                "engagement": {
                    "likes": item.get("likesCount", 0),
                    "comments": item.get("commentsCount", 0)
                },
                "hashtags": item.get("hashtags", []),
                "locations": [item.get("locationName")] if item.get("locationName") else [],
                "author": item.get("ownerUsername", ""),
                "author_followers": item.get("ownerFollowersCount", 0)
            })
        elif platform == "tiktok":
            formatted.update({
                "title": item.get("text", "")[:100],
                "description": item.get("text", ""),
                "url": item.get("webVideoUrl", ""),
                "engagement": {
                    "likes": item.get("diggCount", 0),
                    "comments": item.get("commentCount", 0),
                    "shares": item.get("shareCount", 0),
                    "views": item.get("playCount", 0)
                },
                "hashtags": [c.get("title") for c in item.get("challenges", [])],
                "author": item.get("authorMeta", {}).get("name", ""),
                "author_followers": item.get("authorMeta", {}).get("fans", 0)
            })
        elif platform == "youtube":
            formatted.update({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "url": item.get("url", ""),
                "engagement": {
                    "views": item.get("viewCount", 0),
                    "likes": item.get("likeCount", 0),
                    "comments": item.get("commentCount", 0)
                },
                "author": item.get("channelTitle", "")
            })

        return formatted

    # ==================== Mock Data Methods ====================

    def _get_mock_search_results(self, platform: str, queries: list, limit: int) -> list:
        """Generate mock search results."""
        results = []
        for i, query in enumerate(queries):
            for j in range(min(limit, 3)):
                results.append({
                    "platform": platform,
                    "query": query,
                    "title": f"Amazing {query} Experience #{j+1}",
                    "description": f"Discover the beauty of {query}. This is an amazing travel destination that you must visit!",
                    "url": f"https://{platform}.com/post/{i}_{j}",
                    "engagement": {
                        "likes": 1000 + (j * 500),
                        "comments": 50 + (j * 20),
                        "shares": 100 + (j * 30),
                        "views": 10000 + (j * 2000)
                    },
                    "hashtags": [f"#{query.replace(' ', '')}", "#travel", "#wanderlust", "#explore"],
                    "locations": [query.split()[0] if query.split() else "Unknown"],
                    "author": f"traveler_{i}_{j}",
                    "author_followers": 5000 + (j * 2000),
                    "timestamp": datetime.now().isoformat()
                })
        return results

    def _get_mock_trending(self, platform: str, category: str, limit: int) -> list:
        """Generate mock trending content."""
        trending_topics = [
            "Hidden gems in Portugal",
            "Japanese street food tour",
            "Budget backpacking tips",
            "Luxury resorts in Maldives",
            "Solo travel safety tips"
        ]

        return [
            {
                "platform": platform,
                "title": topic,
                "description": f"Trending content about {topic.lower()}",
                "url": f"https://{platform}.com/trending/{i}",
                "engagement": {
                    "likes": 50000 - (i * 5000),
                    "comments": 2000 - (i * 200),
                    "shares": 5000 - (i * 500),
                    "views": 500000 - (i * 50000)
                },
                "hashtags": [f"#{category}", "#trending", "#travel"],
                "trend_score": 95 - (i * 5)
            }
            for i, topic in enumerate(trending_topics[:limit])
        ]

    def _get_mock_hashtags(self, destination: str, limit: int) -> list:
        """Generate mock trending hashtags."""
        base_hashtags = [
            destination.replace(" ", "").lower(),
            f"{destination.lower()}travel",
            "wanderlust",
            "travelgram",
            "instatravel",
            "explore",
            "vacation",
            "adventure",
            "travelphotography",
            "bucketlist"
        ]

        return [
            {"hashtag": f"#{tag}", "count": 10000 - (i * 500)}
            for i, tag in enumerate(base_hashtags[:limit])
        ]

    def _get_mock_influencer_content(self, destination: str, limit: int) -> list:
        """Generate mock influencer content."""
        influencers = [
            {"name": "TravelWithSarah", "followers": 150000},
            {"name": "NomadJake", "followers": 89000},
            {"name": "WanderlustEmma", "followers": 220000},
            {"name": "AdventureAlex", "followers": 75000},
            {"name": "GlobeTrotterMia", "followers": 180000}
        ]

        return [
            {
                "platform": "instagram",
                "title": f"My {destination} Adventure - Day {i+1}",
                "description": f"Exploring the hidden corners of {destination}. This place is absolutely magical!",
                "url": f"https://instagram.com/p/mock_{i}",
                "author": inf["name"],
                "author_followers": inf["followers"],
                "engagement": {
                    "likes": inf["followers"] // 10,
                    "comments": inf["followers"] // 100
                },
                "hashtags": [f"#{destination.replace(' ', '')}", "#travel", "#sponsored"]
            }
            for i, inf in enumerate(influencers[:limit])
        ]
