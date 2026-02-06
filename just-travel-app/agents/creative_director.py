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
            
            # 2. Production: Generate Poster + Video in Parallel
            # OPTIMIZATION: Run both in parallel for 2min speed improvement
            # Video starts with text-only, fallback to Image-to-Video if needed

            logger.info("Starting parallel media generation (poster + video)")

            # Determine video input: User Upload > None (text-only, fastest)
            video_input_image = uploaded_file if uploaded_file else None

            # Run both tasks in parallel
            poster_task = self.creative_tools.generate_image(poster_prompt)
            video_task = self.creative_tools.generate_video(video_prompt, image_path=video_input_image)

            poster_url, video_url = await asyncio.gather(poster_task, video_task, return_exceptions=True)

            # Handle exceptions
            if isinstance(poster_url, Exception):
                logger.error(f"Poster generation failed: {poster_url}")
                poster_url = ""

            if isinstance(video_url, Exception):
                logger.error(f"Video generation failed: {video_url}")
                video_url = ""

            # Fallback: If video failed and poster succeeded, try Image-to-Video
            if not video_url and poster_url and not uploaded_file:
                logger.info("Video failed, retrying with poster as Image-to-Video input")
                try:
                    video_url = await self.creative_tools.generate_video(video_prompt, image_path=poster_url)
                except Exception as e:
                    logger.error(f"Image-to-Video fallback also failed: {e}")
                    video_url = ""

        except Exception as e:
            logger.error(f"Creative Director failed: {e}")
        
        return {
            "agent": self.name,
            "poster_url": poster_url,
            "video_url": video_url,
            "status": "success"
        }
