"""
Optimizer Agent
===============

This agent creates optimized daily itineraries by combining inputs
from all other agents. It considers timing, geography, user preferences,
and practical constraints to build the best possible travel plan.

The Optimizer handles:
- Daily schedule optimization
- Route efficiency (minimizing travel time)
- Time slot allocation for activities
- Meal planning integration
- Rest and buffer time management

Example Usage:
    optimizer = OptimizerAgent()
    itinerary = optimizer.process("create 3-day itinerary", context)
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class TimeSlot:
    """
    Represents a time slot in the itinerary.

    Attributes:
        start_time: Slot start time
        end_time: Slot end time
        activity_type: Type of activity (attraction, meal, transport, rest)
        activity: The scheduled activity details
        location: Activity location
        notes: Additional notes or tips
    """
    start_time: str
    end_time: str
    activity_type: str
    activity: dict
    location: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DayPlan:
    """
    Represents a single day's itinerary.

    Attributes:
        date: The date of this plan
        day_number: Day number in the trip (1, 2, 3...)
        theme: Optional theme for the day
        time_slots: List of scheduled time slots
        total_travel_time: Estimated travel time between locations
        estimated_cost: Estimated cost for the day
    """
    date: str
    day_number: int
    theme: str = ""
    time_slots: list = field(default_factory=list)
    total_travel_time: int = 0  # minutes
    estimated_cost: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "date": self.date,
            "day_number": self.day_number,
            "theme": self.theme,
            "time_slots": [slot.to_dict() if isinstance(slot, TimeSlot) else slot for slot in self.time_slots],
            "total_travel_time": self.total_travel_time,
            "estimated_cost": self.estimated_cost
        }


class OptimizerAgent:
    """
    Agent responsible for creating optimized travel itineraries.

    The Optimizer takes inputs from all other agents and creates
    a practical, efficient daily schedule that maximizes the
    travel experience while respecting constraints.

    Attributes:
        name: Agent identifier
        description: Brief description of agent capabilities
    """

    # Default time allocations for different activity types (in minutes)
    DEFAULT_DURATIONS = {
        "museum": 120,
        "attraction": 90,
        "landmark": 45,
        "restaurant": 90,
        "cafe": 45,
        "shopping": 60,
        "park": 60,
        "beach": 180,
        "nightlife": 180,
        "transport": 30,
        "rest": 30
    }

    # Typical meal times
    MEAL_TIMES = {
        "breakfast": "08:00",
        "lunch": "12:30",
        "dinner": "19:00"
    }

    # Day structure template
    DAY_STRUCTURE = {
        "early_morning": ("06:00", "09:00"),
        "morning": ("09:00", "12:00"),
        "lunch": ("12:00", "14:00"),
        "afternoon": ("14:00", "18:00"),
        "evening": ("18:00", "21:00"),
        "night": ("21:00", "23:59")
    }

    def __init__(self):
        """Initialize the Optimizer Agent."""
        self.name = "optimizer"
        self.description = "Creates optimized daily itineraries from all inputs"
        logger.info("OptimizerAgent initialized")

    def process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process an itinerary optimization request.

        Args:
            query: User's itinerary request
            context: Context containing profile, destinations, etc.

        Returns:
            dict: Optimized itinerary
        """
        context = context or {}

        # Extract planning parameters
        num_days = self._extract_num_days(query, context)
        start_date = self._extract_start_date(context)

        # Get inputs from other agents
        profile = context.get("profile", {})
        if isinstance(profile, dict) and "profile" in profile:
            profile = profile.get("profile", {})

        destinations = context.get("destinations", {})
        if isinstance(destinations, dict):
            destinations = destinations.get("results", [])

        accommodations = context.get("accommodations", {})
        if isinstance(accommodations, dict):
            accommodations = accommodations.get("results", [])

        trends = context.get("trends", {})
        if isinstance(trends, dict):
            trends = trends.get("trends", [])

        # Build the optimized itinerary
        itinerary = self._build_itinerary(
            num_days=num_days,
            start_date=start_date,
            profile=profile,
            destinations=destinations,
            accommodations=accommodations,
            trends=trends
        )

        response = {
            "agent": self.name,
            "itinerary": [day.to_dict() for day in itinerary],
            "summary": self._generate_summary(itinerary, profile),
            "tips": self._generate_tips(itinerary, profile),
            "total_days": num_days,
            "status": "success" if itinerary else "no_itinerary_generated"
        }

        logger.info(f"Optimizer generated {num_days}-day itinerary")
        return response

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Async version of process for orchestrated workflows.

        Args:
            query: Itinerary request
            context: Session context

        Returns:
            dict: Optimized itinerary
        """
        return self.process(query, context)

    def _extract_num_days(self, query: str, context: dict) -> int:
        """
        Extract the number of days for the itinerary.

        Args:
            query: User's query
            context: Session context with dates

        Returns:
            int: Number of days
        """
        import re

        # Check query for explicit day count
        patterns = [
            r'(\d+)\s*day',
            r'(\d+)\s*night',
            r'(\d+)-day',
            r'week'  # 7 days
        ]

        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                if 'week' in pattern:
                    return 7
                return int(match.group(1))

        # Check context dates
        dates = context.get("dates", {})
        if dates.get("start") and dates.get("end"):
            try:
                start = datetime.fromisoformat(dates["start"])
                end = datetime.fromisoformat(dates["end"])
                return (end - start).days + 1
            except (ValueError, TypeError):
                pass

        # Default to 3 days
        return 3

    def _extract_start_date(self, context: dict) -> datetime:
        """
        Extract or determine the start date.

        Args:
            context: Session context

        Returns:
            datetime: Start date
        """
        dates = context.get("dates", {})
        if dates.get("start"):
            try:
                return datetime.fromisoformat(dates["start"])
            except (ValueError, TypeError):
                pass

        # Default to tomorrow
        return datetime.now() + timedelta(days=1)

    def _build_itinerary(
        self,
        num_days: int,
        start_date: datetime,
        profile: dict,
        destinations: list,
        accommodations: list,
        trends: list
    ) -> list:
        """
        Build the complete itinerary.

        Args:
            num_days: Number of days
            start_date: Trip start date
            profile: User profile
            destinations: Available destinations
            accommodations: Hotel/restaurant options
            trends: Trending activities

        Returns:
            list: List of DayPlan objects
        """
        itinerary = []

        # Prioritize and organize activities
        activities = self._prioritize_activities(
            destinations, accommodations, trends, profile
        )

        # Get restaurants for meals
        restaurants = [a for a in accommodations if "restaurant" in str(a.get("types", []))]

        for day_num in range(1, num_days + 1):
            current_date = start_date + timedelta(days=day_num - 1)

            # Select activities for this day
            day_activities = self._select_day_activities(
                activities, day_num, num_days, profile
            )

            # Build the day plan
            day_plan = self._create_day_plan(
                date=current_date,
                day_number=day_num,
                activities=day_activities,
                restaurants=restaurants,
                profile=profile
            )

            itinerary.append(day_plan)

            # Mark used activities
            for activity in day_activities:
                activity["used"] = True

        return itinerary

    def _prioritize_activities(
        self,
        destinations: list,
        accommodations: list,
        trends: list,
        profile: dict
    ) -> list:
        """
        Prioritize and organize all possible activities.

        Args:
            destinations: Destination list
            accommodations: Accommodations and restaurants
            trends: Trending activities
            profile: User profile

        Returns:
            list: Prioritized activity list
        """
        activities = []
        interests = profile.get("interests", [])

        # Add destinations as activities
        for dest in destinations:
            if isinstance(dest, dict):
                activity = {
                    "name": dest.get("name", "Unknown"),
                    "type": self._categorize_place(dest),
                    "location": dest.get("location", {}),
                    "rating": dest.get("rating", 0),
                    "source": "destination",
                    "priority": self._calculate_priority(dest, interests),
                    "duration": self._estimate_duration(dest),
                    "used": False
                }
                activities.append(activity)

        # Add attractions from accommodations
        for place in accommodations:
            if isinstance(place, dict) and "restaurant" not in str(place.get("types", [])):
                activity = {
                    "name": place.get("name", "Unknown"),
                    "type": self._categorize_place(place),
                    "location": place.get("location", {}),
                    "rating": place.get("rating", 0),
                    "source": "maps",
                    "priority": self._calculate_priority(place, interests),
                    "duration": self._estimate_duration(place),
                    "used": False
                }
                activities.append(activity)

        # Add trending activities
        for trend in trends:
            if isinstance(trend, dict) and trend.get("extracted_locations"):
                activity = {
                    "name": trend.get("title", "Trending Activity"),
                    "type": "trending",
                    "location": {},
                    "trend_score": trend.get("trend_score", 0),
                    "source": "trends",
                    "priority": trend.get("trend_score", 50),
                    "duration": 90,  # Default 90 minutes
                    "used": False
                }
                activities.append(activity)

        # Sort by priority (descending)
        activities.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return activities

    def _categorize_place(self, place: dict) -> str:
        """Categorize a place by type."""
        types = place.get("types", [])
        name = place.get("name", "").lower()

        if any(t in str(types) for t in ["museum", "art_gallery"]):
            return "museum"
        if any(t in str(types) for t in ["park", "natural_feature"]):
            return "park"
        if "beach" in name or "beach" in str(types):
            return "beach"
        if any(t in str(types) for t in ["church", "temple", "mosque"]):
            return "landmark"
        if any(t in str(types) for t in ["shopping", "store"]):
            return "shopping"

        return "attraction"

    def _calculate_priority(self, place: dict, interests: list) -> float:
        """Calculate priority score for an activity."""
        base_score = place.get("rating", 3.0) * 10

        # Boost for matching interests
        place_type = self._categorize_place(place)
        interest_mapping = {
            "cultural": ["museum", "landmark"],
            "nature": ["park", "beach"],
            "adventure": ["park", "attraction"],
            "culinary": ["restaurant"]
        }

        for interest in interests:
            if place_type in interest_mapping.get(interest, []):
                base_score += 15

        # Boost for high review count
        reviews = place.get("user_ratings_total", 0)
        if reviews > 1000:
            base_score += 10
        elif reviews > 500:
            base_score += 5

        return min(base_score, 100)

    def _estimate_duration(self, place: dict) -> int:
        """Estimate visit duration for a place in minutes."""
        place_type = self._categorize_place(place)
        return self.DEFAULT_DURATIONS.get(place_type, 60)

    def _select_day_activities(
        self,
        activities: list,
        day_num: int,
        total_days: int,
        profile: dict
    ) -> list:
        """
        Select activities for a specific day.

        Args:
            activities: All available activities
            day_num: Current day number
            total_days: Total trip days
            profile: User profile

        Returns:
            list: Activities for this day
        """
        # Aim for 4-5 activities per day
        max_activities = 5
        daily_activities = []
        total_duration = 0
        max_duration = 8 * 60  # 8 hours of activities

        # Get unused activities
        available = [a for a in activities if not a.get("used", False)]

        for activity in available:
            if len(daily_activities) >= max_activities:
                break
            if total_duration + activity["duration"] > max_duration:
                continue

            daily_activities.append(activity)
            total_duration += activity["duration"]

        return daily_activities

    def _create_day_plan(
        self,
        date: datetime,
        day_number: int,
        activities: list,
        restaurants: list,
        profile: dict
    ) -> DayPlan:
        """
        Create a structured day plan with time slots.

        Args:
            date: The day's date
            day_number: Day number in trip
            activities: Selected activities
            restaurants: Available restaurants
            profile: User profile

        Returns:
            DayPlan: Complete day plan
        """
        day_plan = DayPlan(
            date=date.strftime("%Y-%m-%d"),
            day_number=day_number,
            theme=self._determine_day_theme(activities)
        )

        current_time = datetime.strptime("09:00", "%H:%M")

        # Morning activities
        morning_activities = activities[:2]
        for activity in morning_activities:
            slot = TimeSlot(
                start_time=current_time.strftime("%H:%M"),
                end_time=(current_time + timedelta(minutes=activity["duration"])).strftime("%H:%M"),
                activity_type=activity["type"],
                activity=activity,
                location=activity.get("name", ""),
                notes=""
            )
            day_plan.time_slots.append(slot)
            current_time += timedelta(minutes=activity["duration"] + 30)  # 30 min buffer

        # Lunch
        lunch_slot = TimeSlot(
            start_time=self.MEAL_TIMES["lunch"],
            end_time="14:00",
            activity_type="meal",
            activity={"name": "Lunch", "type": "meal"},
            location=restaurants[0].get("name", "Local restaurant") if restaurants else "Local restaurant",
            notes="Try local cuisine!"
        )
        day_plan.time_slots.append(lunch_slot)
        current_time = datetime.strptime("14:00", "%H:%M")

        # Afternoon activities
        afternoon_activities = activities[2:]
        for activity in afternoon_activities:
            slot = TimeSlot(
                start_time=current_time.strftime("%H:%M"),
                end_time=(current_time + timedelta(minutes=activity["duration"])).strftime("%H:%M"),
                activity_type=activity["type"],
                activity=activity,
                location=activity.get("name", ""),
                notes=""
            )
            day_plan.time_slots.append(slot)
            current_time += timedelta(minutes=activity["duration"] + 30)

        # Dinner
        dinner_slot = TimeSlot(
            start_time=self.MEAL_TIMES["dinner"],
            end_time="20:30",
            activity_type="meal",
            activity={"name": "Dinner", "type": "meal"},
            location=restaurants[1].get("name", "Local restaurant") if len(restaurants) > 1 else "Local restaurant",
            notes=""
        )
        day_plan.time_slots.append(dinner_slot)

        # Calculate estimated costs based on budget level
        budget_costs = {"budget": 50, "moderate": 100, "luxury": 200}
        day_plan.estimated_cost = budget_costs.get(profile.get("budget_level", "moderate"), 100)

        return day_plan

    def _determine_day_theme(self, activities: list) -> str:
        """Determine a theme for the day based on activities."""
        if not activities:
            return "Exploration Day"

        types = [a.get("type", "") for a in activities]

        if types.count("museum") >= 2:
            return "Culture & History Day"
        if types.count("park") >= 2 or types.count("beach") >= 1:
            return "Nature & Relaxation Day"
        if types.count("shopping") >= 2:
            return "Shopping & Markets Day"
        if "trending" in types:
            return "Local Discoveries Day"

        return "Mixed Adventure Day"

    def _generate_summary(self, itinerary: list, profile: dict) -> dict:
        """Generate a trip summary."""
        total_activities = sum(len(day.time_slots) for day in itinerary)
        total_cost = sum(day.estimated_cost for day in itinerary)

        return {
            "total_days": len(itinerary),
            "total_activities": total_activities,
            "estimated_total_cost": total_cost,
            "budget_level": profile.get("budget_level", "moderate"),
            "day_themes": [day.theme for day in itinerary]
        }

    def _generate_tips(self, itinerary: list, profile: dict) -> list:
        """Generate helpful tips for the trip."""
        tips = [
            "Book popular attractions in advance to avoid long queues",
            "Keep digital copies of all reservations and important documents",
            "Download offline maps for areas with limited connectivity"
        ]

        # Add dietary-specific tips
        dietary = profile.get("dietary_restrictions", []) + profile.get("religious_requirements", [])
        if dietary:
            tips.append(f"Look for restaurants catering to {', '.join(dietary)} dietary needs")

        # Budget-specific tips
        budget = profile.get("budget_level", "moderate")
        if budget == "budget":
            tips.append("Consider getting a city pass for discounted attraction entries")
        elif budget == "luxury":
            tips.append("Book restaurants and premium experiences well in advance")

        return tips
