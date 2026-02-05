"""
Base Agent
==========

This is the foundational class for all specialized agents in the system.
It handles the integration with Google's Gemini models via the
`google-generativeai` SDK.

It supports:
- Model initialization
- "Thought Signature" (native reasoning capability)
- Standardized error handling
"""

import os
import json
import logging
import asyncio
from google import genai
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all AI agents.
    
    Attributes:
        name: The name of the agent (e.g., "profiler", "concierge")
        client: The initialized Gemini Client
        model_name: The name of the model to use
    """
    
    def __init__(self, name: str, description: str, model_type: str = "flash"):
        self.name = name
        self.description = description
        
        # Configure the SDK
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            
        # Select Model based on type
        if model_type == "pro":
            self.model_name = "gemini-3-pro-preview"
        else:
            self.model_name = "gemini-3-flash-preview"
            
        logger.info(f"Agent '{self.name}' initialized with model '{self.model_name}' ({model_type})")

    async def generate_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: The specific instruction/prompt for the agent
            context: Additional context to include (profile, previous thoughts)
            
        Returns:
            str: The raw text response from the model
        """
        try:
            if not self.client:
                return "Error: Client not initialized (Missing API Key)"

            # Construct the full prompt context
            full_prompt = self._construct_prompt(prompt, context)
            
            # Run the synchronous SDK call in a thread to avoid blocking the event loop
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=full_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response for {self.name}: {e}")
            # Fallback or re-raise depending on strategy
            return f"Error: {str(e)}"

    def _construct_prompt(self, base_prompt: str, context: Optional[Dict]) -> str:
        """
        Construct the final prompt by injecting context.
        """
        context_str = ""
        if context:
            context_str = f"\nCONTEXT:\n{context}\n"

        return f"{base_prompt}{context_str}"

    @staticmethod
    def parse_json_response(text: str) -> dict:
        """Strip markdown code fences and parse JSON. Raises json.JSONDecodeError on failure."""
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
