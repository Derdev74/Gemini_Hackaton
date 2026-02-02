"""
Concierge Agent
===============

This agent handles accommodation and restaurant filtering using
the Google Maps/Places API. It provides personalized recommendations
for hotels, restaurants, and other services based on user preferences.

The Concierge filters and recommends:
- Hotels and accommodations
- Restaurants matching dietary preferences
- Local services and amenities
- Verified reviews and ratings

Example Usage:
    concierge = ConciergeAgent()
    hotels = concierge.process("Find halal restaurants near the Eiffel Tower", {})
"""

import logging
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.maps_tools import MapsTools

logger = logging.getLogger(__name__)


class ConciergeAgent:
    """
    Agent responsible for accommodation and dining recommendations.

    The Concierge uses Google Maps/Places API to find and filter
    hotels, restaurants, and services that match user preferences
    including dietary restrictions and budget.

    Attributes:
        name: Agent identifier
        description: Brief description of agent capabilities
        maps_tools: Instance of MapsTools for Google APIs
    """

    # Service type keywords for query classification
    SERVICE_KEYWORDS = {
        "accommodation": [
            "hotel", "hostel", "stay", "accommodation", "lodge",
            "resort", "airbnb", "motel", "inn", "guesthouse", "sleep"
        ],
        "restaurant": [
            "restaurant", "eat", "food", "dining", "dinner", "lunch",
            "breakfast", "cafe", "bistro", "eatery"
        ],
        "attraction": [
            "attraction", "visit", "see", "tour", "museum", "park",
            "landmark", "monument"
        ],
        "transport": [
            "transport", "taxi", "uber", "bus", "train", "metro",
            "airport", "car rental", "bike"
        ]
    }

    # Dietary preference filters
    DIETARY_FILTERS = {
        "halal": ["halal", "muslim friendly"],
        "kosher": ["kosher", "jewish"],
        "vegetarian": ["vegetarian", "veg friendly"],
        "vegan": ["vegan", "plant based", "plant-based"],
        "gluten_free": ["gluten free", "gluten-free", "celiac friendly"]
    }

    # Budget level mapping to price levels (Google's 0-4 scale)
    BUDGET_PRICE_LEVELS = {
        "budget": [0, 1],
        "moderate": [1, 2],
        "luxury": [2, 3, 4]
    }

    def __init__(self):
        """Initialize the Concierge Agent."""
        self.name = "concierge"
        self.description = "Filters and recommends hotels, restaurants using Google Maps"
        self.maps_tools = MapsTools()
        logger.info("ConciergeAgent initialized")

    def process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process a service/accommodation query.

        Args:
            query: User's query about hotels, restaurants, etc.
            context: Optional context with user profile and destinations

        Returns:
            dict: Filtered and ranked recommendations
        """
        context = context or {}
        query_lower = query.lower()

        # Extract user profile preferences
        profile = context.get("profile", {})
        if isinstance(profile, dict) and "profile" in profile:
            profile = profile.get("profile", {})

        # Determine service type
        service_type = self._detect_service_type(query_lower)

        # Extract location
        location = self._extract_location(query_lower, context)

        # Build filters from profile and query
        filters = self._build_filters(query_lower, profile)

        # Search and filter results
        if service_type == "accommodation":
            results = self._find_accommodations(location, filters)
        elif service_type == "restaurant":
            results = self._find_restaurants(location, filters)
        elif service_type == "attraction":
            results = self._find_attractions(location, filters)
        else:
            results = self._general_search(location, query_lower, filters)

        response = {
            "agent": self.name,
            "service_type": service_type,
            "location": location,
            "filters_applied": filters,
            "results": results,
            "result_count": len(results),
            "status": "success" if results else "no_results"
        }

        logger.info(f"Concierge found {len(results)} {service_type} results")
        return response

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Async version of process for use in orchestrated workflows.

        Args:
            query: User's service query
            context: Optional context dictionary

        Returns:
            dict: Filtered recommendations
        """
        return self.process(query, context)

    def _detect_service_type(self, query: str) -> str:
        """
        Detect the type of service being requested.

        Args:
            query: User's query string

        Returns:
            str: Detected service type
        """
        for service_type, keywords in self.SERVICE_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                return service_type

        return "restaurant"  # Default to restaurant searches

    def _extract_location(self, query: str, context: dict) -> Optional[str]:
        """
        Extract location from query or context.

        Args:
            query: User's query string
            context: Session context

        Returns:
            Optional[str]: Location name or coordinates
        """
        # Check context for destinations
        destinations = context.get("destinations", {})
        if isinstance(destinations, dict):
            results = destinations.get("results", [])
            if results and isinstance(results[0], dict):
                return results[0].get("name")

        # Extract from query
        location_indicators = [
            "near ", "in ", "around ", "at ", "by ", "close to "
        ]

        for indicator in location_indicators:
            if indicator in query:
                idx = query.find(indicator) + len(indicator)
                remaining = query[idx:].strip()
                location = remaining.split(",")[0].split("?")[0].strip()
                if location:
                    return location.title()

        return None

    def _build_filters(self, query: str, profile: dict) -> dict:
        """
        Build search filters from query and user profile.

        Args:
            query: User's query string
            profile: User profile dictionary

        Returns:
            dict: Filter configuration
        """
        filters = {
            "dietary": [],
            "price_levels": [0, 1, 2, 3, 4],
            "min_rating": 3.5,
            "open_now": False,
            "accessibility": []
        }

        # Extract dietary filters from profile
        dietary_restrictions = profile.get("dietary_restrictions", [])
        religious_requirements = profile.get("religious_requirements", [])

        all_dietary = dietary_restrictions + religious_requirements
        for restriction in all_dietary:
            if restriction in self.DIETARY_FILTERS:
                filters["dietary"].extend(self.DIETARY_FILTERS[restriction])

        # Also check query for dietary mentions
        for diet_type, keywords in self.DIETARY_FILTERS.items():
            if any(keyword in query for keyword in keywords):
                filters["dietary"].extend(keywords)

        # Remove duplicates
        filters["dietary"] = list(set(filters["dietary"]))

        # Set price levels based on budget
        budget = profile.get("budget_level", "moderate")
        filters["price_levels"] = self.BUDGET_PRICE_LEVELS.get(budget, [0, 1, 2])

        # Check for "open now" requests
        if any(phrase in query for phrase in ["open now", "open right now", "currently open"]):
            filters["open_now"] = True

        # Rating preferences
        if "highly rated" in query or "best rated" in query:
            filters["min_rating"] = 4.5
        elif "top rated" in query:
            filters["min_rating"] = 4.0

        # Accessibility from profile
        accessibility_needs = profile.get("accessibility_needs", [])
        filters["accessibility"] = accessibility_needs

        return filters

    def _find_accommodations(self, location: str, filters: dict) -> list:
        """
        Find accommodations matching filters.

        Args:
            location: Search location
            filters: Filter configuration

        Returns:
            list: Matching accommodations
        """
        if not location:
            return []

        # Search for hotels/accommodations
        raw_results = self.maps_tools.search_places(
            query=f"hotels in {location}",
            place_type="lodging",
            location=location,
            price_levels=filters["price_levels"]
        )

        # Filter and enrich results
        filtered = self._filter_by_rating(raw_results, filters["min_rating"])

        # Get detailed info for top results
        enriched = []
        for place in filtered[:10]:
            details = self.maps_tools.get_place_details(place.get("place_id"))
            enriched.append(self._format_accommodation(place, details))

        return enriched

    def _find_restaurants(self, location: str, filters: dict) -> list:
        """
        Find restaurants matching dietary and budget filters.

        Args:
            location: Search location
            filters: Filter configuration

        Returns:
            list: Matching restaurants
        """
        if not location:
            return []

        # Build search query with dietary requirements
        dietary_query = ""
        if filters["dietary"]:
            dietary_query = " ".join(filters["dietary"][:2])  # Top 2 dietary requirements

        search_query = f"{dietary_query} restaurants in {location}".strip()

        # Search for restaurants
        raw_results = self.maps_tools.search_places(
            query=search_query,
            place_type="restaurant",
            location=location,
            price_levels=filters["price_levels"],
            open_now=filters["open_now"]
        )

        # Filter by rating
        filtered = self._filter_by_rating(raw_results, filters["min_rating"])

        # Additional dietary filtering from reviews/descriptions
        if filters["dietary"]:
            filtered = self._filter_by_dietary(filtered, filters["dietary"])

        # Get detailed info for top results
        enriched = []
        for place in filtered[:10]:
            details = self.maps_tools.get_place_details(place.get("place_id"))
            enriched.append(self._format_restaurant(place, details, filters))

        return enriched

    def _find_attractions(self, location: str, filters: dict) -> list:
        """
        Find tourist attractions at a location.

        Args:
            location: Search location
            filters: Filter configuration

        Returns:
            list: Matching attractions
        """
        if not location:
            return []

        raw_results = self.maps_tools.search_places(
            query=f"tourist attractions in {location}",
            place_type="tourist_attraction",
            location=location
        )

        filtered = self._filter_by_rating(raw_results, filters["min_rating"])

        enriched = []
        for place in filtered[:10]:
            details = self.maps_tools.get_place_details(place.get("place_id"))
            enriched.append(self._format_attraction(place, details))

        return enriched

    def _general_search(self, location: str, query: str, filters: dict) -> list:
        """
        Perform a general place search.

        Args:
            location: Search location
            query: Search query
            filters: Filter configuration

        Returns:
            list: Search results
        """
        if not location:
            return []

        raw_results = self.maps_tools.search_places(
            query=f"{query} in {location}",
            location=location
        )

        return self._filter_by_rating(raw_results, filters["min_rating"])

    def _filter_by_rating(self, places: list, min_rating: float) -> list:
        """
        Filter places by minimum rating.

        Args:
            places: List of places
            min_rating: Minimum acceptable rating

        Returns:
            list: Filtered places
        """
        return [
            place for place in places
            if place.get("rating", 0) >= min_rating
        ]

    def _filter_by_dietary(self, places: list, dietary_keywords: list) -> list:
        """
        Filter places that match dietary requirements.

        Args:
            places: List of places
            dietary_keywords: Keywords to search for

        Returns:
            list: Filtered places matching dietary needs
        """
        filtered = []
        for place in places:
            # Check name, types, and any available descriptions
            place_text = " ".join([
                place.get("name", "").lower(),
                " ".join(place.get("types", [])),
            ])

            # Check if any dietary keyword matches
            if any(keyword.lower() in place_text for keyword in dietary_keywords):
                place["dietary_match"] = True
                filtered.append(place)
            else:
                # Include but mark as unverified
                place["dietary_match"] = False
                filtered.append(place)

        # Sort with dietary matches first
        filtered.sort(key=lambda x: x.get("dietary_match", False), reverse=True)
        return filtered

    def _format_accommodation(self, place: dict, details: dict) -> dict:
        """Format accommodation data for response."""
        return {
            "name": place.get("name"),
            "place_id": place.get("place_id"),
            "rating": place.get("rating"),
            "total_ratings": place.get("user_ratings_total", 0),
            "price_level": place.get("price_level"),
            "address": details.get("formatted_address", place.get("vicinity")),
            "phone": details.get("formatted_phone_number"),
            "website": details.get("website"),
            "location": place.get("geometry", {}).get("location"),
            "amenities": details.get("amenities", []),
            "photos": details.get("photos", [])[:3],
            "reviews_summary": self._summarize_reviews(details.get("reviews", []))
        }

    def _format_restaurant(self, place: dict, details: dict, filters: dict) -> dict:
        """Format restaurant data for response."""
        return {
            "name": place.get("name"),
            "place_id": place.get("place_id"),
            "rating": place.get("rating"),
            "total_ratings": place.get("user_ratings_total", 0),
            "price_level": place.get("price_level"),
            "price_description": self._price_level_to_text(place.get("price_level")),
            "address": details.get("formatted_address", place.get("vicinity")),
            "phone": details.get("formatted_phone_number"),
            "website": details.get("website"),
            "location": place.get("geometry", {}).get("location"),
            "cuisine_types": place.get("types", []),
            "opening_hours": details.get("opening_hours", {}),
            "dietary_verified": place.get("dietary_match", False),
            "dietary_requirements_matched": filters.get("dietary", []),
            "photos": details.get("photos", [])[:3],
            "reviews_summary": self._summarize_reviews(details.get("reviews", []))
        }

    def _format_attraction(self, place: dict, details: dict) -> dict:
        """Format attraction data for response."""
        return {
            "name": place.get("name"),
            "place_id": place.get("place_id"),
            "rating": place.get("rating"),
            "total_ratings": place.get("user_ratings_total", 0),
            "address": details.get("formatted_address", place.get("vicinity")),
            "location": place.get("geometry", {}).get("location"),
            "types": place.get("types", []),
            "opening_hours": details.get("opening_hours", {}),
            "website": details.get("website"),
            "photos": details.get("photos", [])[:3],
            "reviews_summary": self._summarize_reviews(details.get("reviews", []))
        }

    def _price_level_to_text(self, level: Optional[int]) -> str:
        """Convert price level number to text description."""
        descriptions = {
            0: "Free",
            1: "Budget-friendly ($)",
            2: "Moderate ($$)",
            3: "Expensive ($$$)",
            4: "Very Expensive ($$$$)"
        }
        return descriptions.get(level, "Price not available")

    def _summarize_reviews(self, reviews: list) -> dict:
        """
        Summarize reviews into key insights.

        Args:
            reviews: List of review objects

        Returns:
            dict: Review summary
        """
        if not reviews:
            return {"count": 0, "highlights": [], "concerns": []}

        # Simple keyword extraction for highlights/concerns
        positive_keywords = ["excellent", "amazing", "great", "wonderful", "perfect", "best"]
        negative_keywords = ["poor", "bad", "terrible", "dirty", "rude", "slow"]

        highlights = []
        concerns = []

        for review in reviews[:10]:  # Analyze first 10 reviews
            text = review.get("text", "").lower()
            if any(word in text for word in positive_keywords):
                highlights.append(review.get("text", "")[:100])
            if any(word in text for word in negative_keywords):
                concerns.append(review.get("text", "")[:100])

        return {
            "count": len(reviews),
            "average_rating": sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0,
            "highlights": highlights[:3],
            "concerns": concerns[:2]
        }
