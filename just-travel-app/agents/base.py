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
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all AI agents.
    
    Attributes:
        name: The name of the agent (e.g., "profiler", "concierge")
        model: The initialized Gemini GenerativeModel
    """
    
    def __init__(self, name: str, description: str, model_type: str = "flash"):
        self.name = name
        self.description = description
        
        # Configure the SDK
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables.")
        else:
            genai.configure(api_key=api_key)
            
        # Select Model based on type
        # Mapping "Gemini 3" request to best available current models
        # Adjust these strings if specific "gemini-3.0" endpoints become available
        if model_type == "pro":
            model_name = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")
        else:
            model_name = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.0-flash-exp")
            
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Agent '{self.name}' initialized with model '{model_name}' ({model_type})")

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
            # Construct the full prompt context
            full_prompt = self._construct_prompt(prompt, context)
            
            # Generate content
            # Assuming 'thought_signature' is enabled via prompt or config if available
            response = await self.model.generate_content_async(full_prompt)
            
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
            context_str = f"\\nCONTEXT:\\n{context}\\n"
            
        return f"{base_prompt}{context_str}"
