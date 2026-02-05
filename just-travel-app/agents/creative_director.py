import logging
import asyncio
from typing import Optional, Dict
from agents.base import BaseAgent
from tools.creative_tools import CreativeTools

logger = logging.getLogger(__name__)

class CreativeDirectorAgent(BaseAgent):
    """
    Agent responsible for generating visual assets ("The Commercial") for the trip.
    """

    def __init__(self):
        super().__init__(name="creative_director", description="Generates visual previews", model_type="pro")
        self.creative_tools = CreativeTools()
        logger.info("CreativeDirectorAgent initialized.")

    async def async_process(self, plan_data: Dict, context: Optional[dict] = None) -> Dict:
        """
        Analyze the itinerary and generate a poster and a video.
        """
        logger.info("Creative Director starting production...")
        
        context = context or {}
        
        # 1. Extract Visual Concept
        # We assume 'plan_data' is the dictionary returned by the Optimizer
        itinerary_summary = plan_data.get("summary", "")
        if not itinerary_summary and "itinerary" in plan_data:
             itinerary_summary = str(plan_data["itinerary"])

        # Check for user uploads to use as reference
        # We look for a key 'uploaded_file' in the context
        uploaded_file = context.get("uploaded_file")
        
        prompt = f"""
        You are a visionary film director for travel commercials.
        
        Itinerary Summary: "{itinerary_summary}"
        User Context: {context.get("profile", {})}
        
        Task:
        1. Create a prompt for a "Cinematic Travel Poster" that captures the essence of this trip.
        2. Create a prompt for a "Teaser Video" (8 seconds) that shows the highlight of the trip.
        
        Output JSON ONLY:
        {{
            "poster_prompt": "A high-resolution, sunlight-drenched shot of...",
            "video_prompt": "Drone shot flying over...",
            "mood": "Adventurous/Relaxing/Luxury"
        }}
        """
        
        response_text = await self.generate_response(prompt, context=context)
        
        poster_url = ""
        video_url = ""
        
        try:
            concept = self.parse_json_response(response_text)
            
            poster_prompt = concept.get("poster_prompt", f"Travel poster for {itinerary_summary[:20]}")
            video_prompt = concept.get("video_prompt", f"Cinematic video of {itinerary_summary[:20]}")
            
            # 2. Production: Generate Poster
            # We run these sequentially or parallel. Parallel is better for speed, 
            # BUT if we want to use the poster as input for the video (Image-to-Video), we must do sequential.
            # User doc showed Image-to-Video is powerful. Let's try that flow if no upload is present.
            
            # A. Generate Poster
            poster_url = await self.creative_tools.generate_image(poster_prompt)
            
            # B. Generate Video
            # If user uploaded a file, use that as the anchor image for the video?
            # Or use the generated poster?
            # Let's prioritize User Upload > Generated Poster > Text Only
            
            video_input_image = uploaded_file if uploaded_file else poster_url
            
            # Note: uploaded_file should be a relative path like "/uploads/foo.png" 
            # creative_tools handles resolving this.
            
            video_url = await self.creative_tools.generate_video(video_prompt, image_path=video_input_image)

        except Exception as e:
            logger.error(f"Creative Director failed: {e}")
        
        return {
            "agent": self.name,
            "poster_url": poster_url,
            "video_url": video_url,
            "status": "success"
        }
