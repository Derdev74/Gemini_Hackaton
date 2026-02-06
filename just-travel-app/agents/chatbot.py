# backend/agents/chatbot.py

import logging
import json
from typing import Optional
from agents.base import BaseAgent
from agents.optimizer import OptimizerAgent  # Import your existing Optimizer

logger = logging.getLogger(__name__)

class ChatbotAgent(BaseAgent):
    def __init__(self):
        # We use a "pro" model for the Chatbot because it needs high empathy and logic
        super().__init__(name="chatbot", description="Main interface for user reassurance and orchestration", model_type="pro")
        self.optimizer = OptimizerAgent()
        logger.info("ChatbotAgent initialized")

    async def async_process(self, user_query: str, context: Optional[dict] = None) -> dict:
        context = context or {}
        
        # 1. First, ask the LLM to decide: "Does this user need a new itinerary or just reassurance?"
        # We use a "Router" prompt strategy
        intent_prompt = f"""
        You are the 'Just Travel' Concierge. Your job is to support first-time travelers.
        User said: "{user_query}"

        DECIDE THE INTENT:
        - If the user wants to change their budget, destination, or dates: Output "OPTIMIZE"
        - If the user is anxious, asking basic questions, or needs reassurance: Output "CHAT"
        
        Output only the word "OPTIMIZE" or "CHAT".
        """
        
        intent = await self.generate_response(intent_prompt)
        intent = intent.strip().upper()

        # 2. ROUTE THE TASK
        if "OPTIMIZE" in intent:
            logger.info("Chatbot detected a change request. Calling Optimizer...")
            # We call the Optimizer's process and then wrap its answer in a reassuring message
            new_itinerary = await self.optimizer.async_process(user_query, context)
            
            reassurance_prompt = f"""
            The user wants to change their plan. I found a new optimized itinerary: {json.dumps(new_itinerary)}
            
            Write a very warm, reassuring response to the user. 
            Explain that you've consulted the 'Just Travel Optimizer' and found a great new plan.
            Summarize the new plan briefly and tell them you've updated their view.
            """
            final_text = await self.generate_response(reassurance_prompt)
            return {"text": final_text, "data": new_itinerary, "type": "optimization_update"}

        else:
            # 3. JUST REASSURE
            logger.info("Chatbot is providing standard reassurance.")
            chat_prompt = f"""
            User Query: "{user_query}"
            Context: {json.dumps(context.get('profile', {}))}
            
            You are a kind, empathetic travel expert. 
            Answer their question and specifically address the anxiety of a first-time traveler. 
            Use phrases like "It's totally normal to wonder about that" or "I've got your back."
            """
            REASSURANCE_PROMPT = """
            You are the 'Just Travel' Lead Concierge. Your specialty is supporting first-time 
            international travelers who are anxious about planning.

            YOUR RULES:
            1. ACKNOWLEDGE EMOTION: If a user sounds worried, start with: "It's totally normal 
            to feel overwhelmed by [X]."
            2. SIMPLIFY: Break down complex travel jargon (like 'layovers' or 'VAT refunds').
            3. THE HANDOFF: If you need to change the itinerary, say: "I'm asking our 
            Optimization Engine to crunch the numbers to keep you safe and on budget."
            4. DIETARY SAFETY: If they mention food allergies, be extra protective. 
            "I'll make sure we find spots where you don't have to worry about [Allergy]."
            """
            response_text = await self.generate_response(chat_prompt)
            return {"text": response_text, "type": "standard_chat"}