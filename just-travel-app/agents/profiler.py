"""
Profiler Agent
==============

This agent captures and manages user preferences, dietary restrictions,
religious constraints, and travel style preferences.

The Profiler is typically the first agent to interact with users,
building a comprehensive profile that informs all other agents'
recommendations.

Example Usage:
    profiler = ProfilerAgent()
    profile = profiler.process("I'm vegetarian and prefer budget travel", {})
"""

import logging
from typing import Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class TravelerProfile:
    """
    Data class representing a traveler's complete profile.

    Attributes:
        dietary_restrictions: List of dietary constraints (vegetarian, vegan, etc.)
        religious_requirements: Religious dietary/travel requirements (halal, kosher)
        allergies: Food allergies to avoid
        budget_level: Travel budget preference (budget, moderate, luxury)
        travel_style: Preferred travel style (adventure, relaxation, cultural)
        accessibility_needs: Any accessibility requirements
        group_size: Number of travelers
        interests: List of travel interests
        language_preferences: Preferred languages for communication
    """
    dietary_restrictions: list = field(default_factory=list)
    religious_requirements: list = field(default_factory=list)
    allergies: list = field(default_factory=list)
    budget_level: str = "moderate"
    travel_style: str = "balanced"
    accessibility_needs: list = field(default_factory=list)
    group_size: int = 1
    interests: list = field(default_factory=list)
    language_preferences: list = field(default_factory=lambda: ["English"])

    def to_dict(self) -> dict:
        """Convert profile to dictionary format."""
        return asdict(self)


class ProfilerAgent:
    """
    Agent responsible for capturing and managing user travel profiles.

    The Profiler extracts user preferences from natural language input
    and maintains a structured profile that other agents can use to
    personalize their recommendations.

    Attributes:
        name: Agent identifier
        description: Brief description of agent capabilities
        current_profile: The active traveler profile being built
    """

    # Keywords for detecting different profile aspects
    DIETARY_KEYWORDS = {
        "vegetarian": "vegetarian",
        "vegan": "vegan",
        "pescatarian": "pescatarian",
        "gluten-free": "gluten_free",
        "gluten free": "gluten_free",
        "dairy-free": "dairy_free",
        "dairy free": "dairy_free",
        "lactose": "dairy_free",
        "no meat": "vegetarian",
        "plant-based": "vegan",
        "plant based": "vegan"
    }

    RELIGIOUS_KEYWORDS = {
        "halal": "halal",
        "kosher": "kosher",
        "hindu": "hindu_dietary",
        "buddhist": "buddhist_dietary",
        "jain": "jain_dietary"
    }

    BUDGET_KEYWORDS = {
        "budget": "budget",
        "cheap": "budget",
        "affordable": "budget",
        "backpack": "budget",
        "moderate": "moderate",
        "mid-range": "moderate",
        "luxury": "luxury",
        "premium": "luxury",
        "high-end": "luxury",
        "expensive": "luxury",
        "splurge": "luxury"
    }

    TRAVEL_STYLE_KEYWORDS = {
        "adventure": "adventure",
        "adventurous": "adventure",
        "relaxation": "relaxation",
        "relaxing": "relaxation",
        "peaceful": "relaxation",
        "cultural": "cultural",
        "culture": "cultural",
        "historical": "cultural",
        "foodie": "culinary",
        "culinary": "culinary",
        "food tour": "culinary",
        "nature": "nature",
        "outdoor": "nature",
        "hiking": "nature",
        "beach": "beach",
        "coastal": "beach",
        "nightlife": "nightlife",
        "party": "nightlife",
        "family": "family_friendly",
        "kid": "family_friendly",
        "romantic": "romantic",
        "honeymoon": "romantic"
    }

    ALLERGY_KEYWORDS = [
        "allergy", "allergic", "can't eat", "cannot eat",
        "intolerant", "intolerance"
    ]

    def __init__(self):
        """Initialize the Profiler Agent."""
        self.name = "profiler"
        self.description = "Captures user dietary, religious, and travel preferences"
        self.current_profile = TravelerProfile()
        logger.info(f"ProfilerAgent initialized")

    def process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process a user query to extract and update profile information.

        Args:
            query: User's natural language input
            context: Optional context with existing session data

        Returns:
            dict: Updated profile and any clarifying questions
        """
        context = context or {}
        query_lower = query.lower()

        # Extract profile information from query
        self._extract_dietary(query_lower)
        self._extract_religious(query_lower)
        self._extract_budget(query_lower)
        self._extract_travel_style(query_lower)
        self._extract_allergies(query_lower)
        self._extract_group_size(query_lower)

        # Build response
        response = {
            "agent": self.name,
            "profile": self.current_profile.to_dict(),
            "extracted_preferences": self._summarize_extractions(query_lower),
            "follow_up_questions": self._generate_follow_up_questions(),
            "status": "profile_updated"
        }

        logger.info(f"Profile updated: {response['extracted_preferences']}")
        return response

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Async version of process for use in orchestrated workflows.

        Args:
            query: User's natural language input
            context: Optional context with existing session data

        Returns:
            dict: Updated profile and any clarifying questions
        """
        return self.process(query, context)

    def _extract_dietary(self, query: str) -> None:
        """Extract dietary restrictions from query."""
        for keyword, restriction in self.DIETARY_KEYWORDS.items():
            if keyword in query:
                if restriction not in self.current_profile.dietary_restrictions:
                    self.current_profile.dietary_restrictions.append(restriction)
                    logger.debug(f"Extracted dietary restriction: {restriction}")

    def _extract_religious(self, query: str) -> None:
        """Extract religious dietary requirements from query."""
        for keyword, requirement in self.RELIGIOUS_KEYWORDS.items():
            if keyword in query:
                if requirement not in self.current_profile.religious_requirements:
                    self.current_profile.religious_requirements.append(requirement)
                    logger.debug(f"Extracted religious requirement: {requirement}")

    def _extract_budget(self, query: str) -> None:
        """Extract budget preference from query."""
        for keyword, level in self.BUDGET_KEYWORDS.items():
            if keyword in query:
                self.current_profile.budget_level = level
                logger.debug(f"Extracted budget level: {level}")
                break

    def _extract_travel_style(self, query: str) -> None:
        """Extract travel style preferences from query."""
        for keyword, style in self.TRAVEL_STYLE_KEYWORDS.items():
            if keyword in query:
                if style not in self.current_profile.interests:
                    self.current_profile.interests.append(style)
                    logger.debug(f"Extracted travel style: {style}")

    def _extract_allergies(self, query: str) -> None:
        """Extract food allergies from query."""
        # Check if query mentions allergies
        has_allergy_mention = any(kw in query for kw in self.ALLERGY_KEYWORDS)

        if has_allergy_mention:
            # Common allergens to detect
            common_allergens = [
                "peanut", "nut", "shellfish", "seafood", "egg",
                "soy", "wheat", "milk", "fish", "sesame"
            ]
            for allergen in common_allergens:
                if allergen in query:
                    if allergen not in self.current_profile.allergies:
                        self.current_profile.allergies.append(allergen)
                        logger.debug(f"Extracted allergy: {allergen}")

    def _extract_group_size(self, query: str) -> None:
        """Extract group size from query."""
        import re

        # Look for patterns like "2 people", "family of 4", "solo"
        solo_patterns = ["solo", "alone", "by myself", "just me"]
        if any(pattern in query for pattern in solo_patterns):
            self.current_profile.group_size = 1
            return

        couple_patterns = ["couple", "two of us", "partner and i", "my partner"]
        if any(pattern in query for pattern in couple_patterns):
            self.current_profile.group_size = 2
            return

        # Look for numeric patterns
        number_match = re.search(r'(\d+)\s*(people|persons|travelers|of us)', query)
        if number_match:
            self.current_profile.group_size = int(number_match.group(1))

    def _summarize_extractions(self, query: str) -> list:
        """Summarize what was extracted from the query."""
        extractions = []

        if self.current_profile.dietary_restrictions:
            extractions.append(f"Dietary: {', '.join(self.current_profile.dietary_restrictions)}")

        if self.current_profile.religious_requirements:
            extractions.append(f"Religious: {', '.join(self.current_profile.religious_requirements)}")

        if self.current_profile.allergies:
            extractions.append(f"Allergies: {', '.join(self.current_profile.allergies)}")

        extractions.append(f"Budget: {self.current_profile.budget_level}")

        if self.current_profile.interests:
            extractions.append(f"Interests: {', '.join(self.current_profile.interests)}")

        extractions.append(f"Group size: {self.current_profile.group_size}")

        return extractions

    def _generate_follow_up_questions(self) -> list:
        """Generate follow-up questions to complete the profile."""
        questions = []

        if not self.current_profile.dietary_restrictions and not self.current_profile.religious_requirements:
            questions.append("Do you have any dietary restrictions or food preferences I should know about?")

        if not self.current_profile.interests:
            questions.append("What type of travel experience are you looking for? (adventure, relaxation, cultural, etc.)")

        if self.current_profile.group_size == 1:
            questions.append("Will you be traveling solo, or with others?")

        return questions

    def get_profile(self) -> TravelerProfile:
        """Get the current traveler profile."""
        return self.current_profile

    def reset_profile(self) -> None:
        """Reset the profile to defaults."""
        self.current_profile = TravelerProfile()
        logger.info("Profile reset to defaults")
