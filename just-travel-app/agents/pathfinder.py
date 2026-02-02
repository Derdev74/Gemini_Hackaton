import logging
import json
import sys
import os
from typing import Optional
from agents.base import BaseAgent

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.cypher_tools import CypherTools
from tools.transport_tools import TransportTools

logger = logging.getLogger(__name__)

class PathfinderAgent(BaseAgent):
    """
    Agent responsible for destination discovery using LLM and Graph DB.
    """

    def __init__(self):
        super().__init__(name="pathfinder", description="Finds destinations using LLM + Graph", model_type="pro")
        self.cypher_tools = CypherTools()
        self.transport_tools = TransportTools()
        logger.info("PathfinderAgent initialized with LLM and Transport Tools")

    async def async_process(self, query: str, context: Optional[dict] = None) -> dict:
        """
        Process a destination query using LLM to decide on the tool call.
        """
        context = context or {}
        
        # 1. LLM Reasoning Step
        prompt = f"""
        You are an expert travel graph navigator.
        
        User Query: "{query}"
        User Profile: {context.get("profile", {})}
        
        Your Goal: Determine the best tool to call to answer the user's request.
        
        Available Tools:
        - search_flights(origin, destination, departure_date) -> Use when user asks for flights or transport.
        - find_by_category(category, location, limit)
        - find_destinations_in_region(region, limit)
        - find_nearby_destinations(location, max_distance_km, limit)
        - find_connected_destinations(location, connection_types, limit)
        - search_destinations(categories, location, budget, limit)
        
        Output JSON ONLY:
        {{
            "intent": "reasoning about what the user wants",
            "tool_call": "name_of_function",
            "arguments": {{
                "arg1": "value1",
                ...
            }}
        }}
        """
        
        response_text = await self.generate_response(prompt, context=context)
        
        results = []
        intent = "unknown"
        
        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            decision = json.loads(clean_text)
            
            intent = decision.get("intent", "")
            tool_name = decision.get("tool_call")
            args = decision.get("arguments", {})
            
            logger.info(f"Pathfinder deciding to call: {tool_name} with {args}")
            
            # 2. Execute Tool
            if tool_name == "search_flights":
                results = self.transport_tools.search_flights(**args)
            elif tool_name == "find_by_category":
                results = self.cypher_tools.find_by_category(**args)
            elif tool_name == "find_destinations_in_region":
                results = self.cypher_tools.find_destinations_in_region(**args)
            elif tool_name == "find_nearby_destinations":
                results = self.cypher_tools.find_nearby_destinations(**args)
            elif tool_name == "find_connected_destinations":
                results = self.cypher_tools.find_connected_destinations(**args)
            elif tool_name == "search_destinations":
                results = self.cypher_tools.search_destinations(**args)
            else:
                # Fallback
                results = self.cypher_tools.search_destinations(location=args.get("location"))

        except Exception as e:
            logger.error(f"Pathfinder error: {e}")
            results = []

        return {
            "agent": self.name,
            "intent": intent,
            "results": results,
            "result_count": len(results),
            "status": "success" if results else "no_results"
        }
