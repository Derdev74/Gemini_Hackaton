"""
Pathfinder Agent
================

This agent handles all graph database operations using Neo4j.
It constructs and executes Cypher queries to find destinations,
routes, and connections between travel locations.

The Pathfinder uses the Neo4j graph to:
- Find destinations matching user preferences
- Discover connections between places
- Calculate optimal routes
- Find nearby attractions

Example Usage:
    pathfinder = PathfinderAgent()
    results = pathfinder.process("Find destinations near Paris with museums", {})
"""

import logging
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.cypher_tools import CypherTools

logger = logging.getLogger(__name__)


class PathfinderAgent:
    """
    Agent responsible for graph database queries and destination discovery.

    The Pathfinder translates natural language queries into Cypher queries
    for Neo4j, enabling powerful graph-based destination recommendations.

    Attributes:
        name: Agent identifier
        description: Brief description of agent capabilities
        cypher_tools: Instance of CypherTools for database operations
    """

    # Query intent patterns for routing
    QUERY_PATTERNS = {
        "find_destinations": [
            "find", "search", "looking for", "show me", "recommend",
            "suggest", "discover", "explore"
        ],
        "find_nearby": [
            "nearby", "near", "close to", "around", "within",
            "distance", "from"
        ],
        "find_route": [
            "route", "path", "way", "direction", "travel from",
            "get to", "how to reach"
        ],
        "find_connections": [
            "connected", "connection", "related", "similar",
            "like", "also visit"
        ]
    }

    # Category mappings for destinations
    CATEGORY_KEYWORDS = {
        "museum": "MUSEUM",
        "art": "MUSEUM",
        "history": "HISTORICAL",
        "historical": "HISTORICAL",
        "ancient": "HISTORICAL",
        "beach": "BEACH",
        "coast": "BEACH",
        "ocean": "BEACH",
        "mountain": "MOUNTAIN",
        "hiking": "MOUNTAIN",
        "nature": "NATURE",
        "park": "NATURE",
        "wildlife": "NATURE",
        "food": "CULINARY",
        "restaurant": "CULINARY",
        "cuisine": "CULINARY",
        "nightlife": "NIGHTLIFE",
        "bar": "NIGHTLIFE",
        "club": "NIGHTLIFE",
        "shopping": "SHOPPING",
        "market": "SHOPPING",
        "temple": "RELIGIOUS",
        "church": "RELIGIOUS",
        "mosque": "RELIGIOUS",
        "spiritual": "RELIGIOUS"
    }

    def __init__(self):
        """Initialize the Pathfinder Agent."""
        self.name = "pathfinder"
        self.description = "Handles Neo4j graph queries for destination discovery"
        self.cypher_tools = CypherTools()
        logger.info("PathfinderAgent initialized")

    def process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process a destination query and return relevant locations.

        Args:
            query: User's natural language query about destinations
            context: Optional context with user profile and preferences

        Returns:
            dict: Matching destinations and recommendations
        """
        context = context or {}
        query_lower = query.lower()

        # Determine query intent
        intent = self._determine_intent(query_lower)
        logger.info(f"Query intent determined: {intent}")

        # Extract query parameters
        params = self._extract_query_params(query_lower, context)

        # Execute appropriate query based on intent
        if intent == "find_destinations":
            results = self._find_destinations(params)
        elif intent == "find_nearby":
            results = self._find_nearby(params)
        elif intent == "find_route":
            results = self._find_route(params)
        elif intent == "find_connections":
            results = self._find_connections(params)
        else:
            results = self._general_search(params)

        response = {
            "agent": self.name,
            "intent": intent,
            "query_params": params,
            "results": results,
            "result_count": len(results) if isinstance(results, list) else 1,
            "status": "success" if results else "no_results"
        }

        logger.info(f"Pathfinder returned {response['result_count']} results")
        return response

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Async version of process for use in orchestrated workflows.

        Args:
            query: User's natural language query
            context: Optional context dictionary

        Returns:
            dict: Query results
        """
        return self.process(query, context)

    def _determine_intent(self, query: str) -> str:
        """
        Determine the intent of the user's query.

        Args:
            query: Lowercase query string

        Returns:
            str: Detected intent category
        """
        for intent, keywords in self.QUERY_PATTERNS.items():
            if any(keyword in query for keyword in keywords):
                return intent
        return "find_destinations"  # Default intent

    def _extract_query_params(self, query: str, context: dict) -> dict:
        """
        Extract parameters from the query for Cypher construction.

        Args:
            query: User's query string
            context: Session context with profile info

        Returns:
            dict: Extracted parameters for query construction
        """
        params = {
            "categories": [],
            "location": None,
            "budget": context.get("profile", {}).get("budget_level", "moderate"),
            "max_distance": None,
            "limit": 10
        }

        # Extract categories
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in query:
                if category not in params["categories"]:
                    params["categories"].append(category)

        # Extract location names (basic extraction)
        # In production, use NER for better extraction
        location_indicators = ["in ", "near ", "around ", "to ", "from "]
        for indicator in location_indicators:
            if indicator in query:
                # Extract word after indicator
                idx = query.find(indicator) + len(indicator)
                remaining = query[idx:].strip()
                # Take first word or words until punctuation
                location = remaining.split(",")[0].split(".")[0].strip()
                if location:
                    params["location"] = location.title()
                    break

        # Extract distance if mentioned
        import re
        distance_match = re.search(r'(\d+)\s*(km|miles?|kilometers?)', query)
        if distance_match:
            params["max_distance"] = int(distance_match.group(1))

        return params

    def _find_destinations(self, params: dict) -> list:
        """
        Find destinations matching the given parameters.

        Args:
            params: Query parameters

        Returns:
            list: Matching destinations
        """
        categories = params.get("categories", [])
        location = params.get("location")
        limit = params.get("limit", 10)

        if categories:
            return self.cypher_tools.find_by_category(
                categories[0],  # Primary category
                location=location,
                limit=limit
            )
        elif location:
            return self.cypher_tools.find_destinations_in_region(
                location,
                limit=limit
            )
        else:
            return self.cypher_tools.get_popular_destinations(limit=limit)

    def _find_nearby(self, params: dict) -> list:
        """
        Find destinations near a specified location.

        Args:
            params: Query parameters with location

        Returns:
            list: Nearby destinations
        """
        location = params.get("location")
        max_distance = params.get("max_distance", 50)  # Default 50km

        if not location:
            return []

        return self.cypher_tools.find_nearby_destinations(
            location,
            max_distance_km=max_distance,
            limit=params.get("limit", 10)
        )

    def _find_route(self, params: dict) -> list:
        """
        Find route between destinations.

        Args:
            params: Query parameters with start/end locations

        Returns:
            list: Route information
        """
        # For route finding, we need start and end
        # This is a simplified implementation
        location = params.get("location")

        if not location:
            return []

        return self.cypher_tools.find_route_suggestions(
            start_location=location,
            preferences=params.get("categories", [])
        )

    def _find_connections(self, params: dict) -> list:
        """
        Find connected or related destinations.

        Args:
            params: Query parameters

        Returns:
            list: Connected destinations
        """
        location = params.get("location")

        if not location:
            return []

        return self.cypher_tools.find_connected_destinations(
            location,
            connection_types=["NEAR", "SIMILAR_TO", "RECOMMENDED_WITH"],
            limit=params.get("limit", 10)
        )

    def _general_search(self, params: dict) -> list:
        """
        Perform a general search across all destinations.

        Args:
            params: Query parameters

        Returns:
            list: Search results
        """
        return self.cypher_tools.search_destinations(
            categories=params.get("categories"),
            location=params.get("location"),
            budget=params.get("budget"),
            limit=params.get("limit", 10)
        )

    def execute_custom_query(self, cypher_query: str, parameters: dict = None) -> list:
        """
        Execute a custom Cypher query directly.

        Args:
            cypher_query: Raw Cypher query string
            parameters: Query parameters

        Returns:
            list: Query results
        """
        return self.cypher_tools.execute_query(cypher_query, parameters or {})
