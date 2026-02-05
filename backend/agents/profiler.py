"""
Profiler Agent
==============

This agent uses Gemini 3 to extract user preferences, dietary restrictions,
and travel style from natural language input.
"""

import logging
import json
import re
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class TravelerProfile:
    """
    Data class representing a traveler's complete profile.
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
        return asdict(self)


class ProfilerAgent(BaseAgent):
    """
    Agent responsible for capturing and managing user travel profiles using LLM.
    """

    def __init__(self):
        super().__init__(name="profiler", description="Captures user preferences using LLM", model_type="flash")
        self.current_profile = TravelerProfile()
        logger.info(f"ProfilerAgent initialized with LLM")

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process a user query to extract profile information using LLM.
        """
        context = context or {}
        
        # Construct Prompt
        prompt = f"""
        Analyze the following user input and extract travel profile information.
        
        User Input: "{query}"
        
        Current Profile State:
        {json.dumps(self.current_profile.to_dict(), indent=2)}
        
        Task:
        1. Identify any NEW or UPDATED:
           - dietary_restrictions (e.g., vegetarian, vegan)
           - religious_requirements (e.g., halal, kosher)
           - allergies
           - budget_level (budget, moderate, luxury)
           - travel_style (adventure, relaxation, cultural, etc.)
           - group_size
           - interests
        2. Merge with the Current Profile State.
        3. Highlight what specifically changed.
        4. Generate 1-2 relevant follow-up questions if critical info is missing.
        
        Output JSON format ONLY:
        {{
            "profile": {{ ...complete profile object... }},
            "changes": ["list of fields changed"],
            "follow_up_questions": ["question 1"]
        }}
        """
        
        # Call LLM
        response_text = await self.generate_response(prompt, context=context)
        
        # Parse result
        try:
            # Simple cleanup for potential markdown code blocks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
            # Update internal state
            new_profile_data = data.get("profile", {})
            self._update_profile(new_profile_data)
            
            return {
                "agent": self.name,
                "profile": self.current_profile.to_dict(),
                "extracted_preferences": data.get("changes", []),
                "follow_up_questions": data.get("follow_up_questions", []),
                "status": "profile_updated"
            }
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response_text}")
            # Fallback to returning current state with a generic message
            return {
                "agent": self.name,
                "profile": self.current_profile.to_dict(),
                "extracted_preferences": [],
                "follow_up_questions": ["Could you provide more details about your trip?"],
                "status": "error_parsing_llm"
            }

    def _update_profile(self, new_data: dict):
        """Update the dataclass with new dictionary data."""
        for key, value in new_data.items():
            if hasattr(self.current_profile, key):
                current_attr = getattr(self.current_profile, key)
                # If both are lists, extend to avoid losing previous data (e.g. existing allergies)
                if isinstance(current_attr, list) and isinstance(value, list):
                    # Use set to avoid duplicates while merging
                    merged = list(set(current_attr + value))
                    setattr(self.current_profile, key, merged)
                else:
                    # Simple overwrite for scalars
                    setattr(self.current_profile, key, value)
