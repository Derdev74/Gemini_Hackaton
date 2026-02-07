import logging
import asyncio
from typing import Optional, Dict, List
from agents.base import BaseAgent
from tools.creative_tools import CreativeTools

logger = logging.getLogger(__name__)

# Maximum number of daily posters to generate (even for longer trips)
MAX_DAILY_POSTERS = 5


class CreativeDirectorAgent(BaseAgent):
    """
    Agent responsible for generating visual assets ("The Commercial") for the trip.

    Generates:
    - 1 trip overview poster
    - Up to 5 daily posters (one per day, max 5)
    - 1 promotional video (8 seconds)
    """

    def __init__(self):
        super().__init__(name="creative_director", description="Generates visual previews", model_type="pro")
        self.creative_tools = CreativeTools()
        logger.info("CreativeDirectorAgent initialized.")

    async def async_process(self, plan_data: Dict, context: Optional[dict] = None) -> Dict:
        """
        Analyze the itinerary and generate daily posters, trip poster, and video.
        """
        logger.info("Creative Director starting production...")

        context = context or {}

        # Extract itinerary data from Optimizer output
        daily_itinerary = plan_data.get("daily_itinerary", [])
        trip_title = plan_data.get("trip_title", "Your Amazing Trip")
        trip_visual_theme = plan_data.get("trip_visual_theme", "Adventure awaits")
        itinerary_summary = plan_data.get("summary", "")

        # Check for user uploads
        uploaded_file = context.get("uploaded_file")

        # Limit daily posters to MAX_DAILY_POSTERS
        days_to_render = daily_itinerary[:MAX_DAILY_POSTERS]
        num_days = len(days_to_render)

        logger.info(f"Generating {num_days} daily posters + 1 trip poster + 1 video")

        # 1. Generate prompts for daily posters
        daily_poster_prompts = []
        for day in days_to_render:
            day_num = day.get("day_number", 1)
            theme = day.get("theme", "Exploration")
            highlight = day.get("daily_highlight", "")
            visual_theme = day.get("visual_theme", "Vibrant and exciting")
            key_locations = day.get("key_locations", [])

            prompt = f"""
            Cinematic travel poster for Day {day_num}: {theme}
            Highlight moment: {highlight}
            Visual mood: {visual_theme}
            Featured locations: {', '.join(key_locations) if key_locations else 'scenic destination'}
            Style: High-resolution, professional travel photography, golden hour lighting
            """
            daily_poster_prompts.append((day_num, prompt.strip()))

        # 2. Generate trip overview poster prompt
        trip_poster_prompt = f"""
        Stunning cinematic travel poster for "{trip_title}"
        Theme: {trip_visual_theme}
        Summary: {itinerary_summary[:200] if itinerary_summary else 'An unforgettable journey'}
        Style: Epic wide-angle shot, professional travel photography, dramatic lighting,
        captures the essence of the entire trip in one breathtaking image
        """

        # 3. Generate all posters in parallel
        poster_tasks = []

        # Daily poster tasks
        for day_num, prompt in daily_poster_prompts:
            poster_tasks.append(self.creative_tools.generate_image(prompt))

        # Trip poster task (added last)
        poster_tasks.append(self.creative_tools.generate_image(trip_poster_prompt.strip()))

        logger.info(f"Starting parallel generation of {len(poster_tasks)} posters...")
        poster_results = await asyncio.gather(*poster_tasks, return_exceptions=True)

        # 4. Parse poster results
        daily_posters: List[Dict] = []
        for i, (day_num, _) in enumerate(daily_poster_prompts):
            result = poster_results[i]
            if isinstance(result, Exception):
                logger.error(f"Day {day_num} poster failed: {result}")
                url = ""
            else:
                url = result or ""
            daily_posters.append({"day": day_num, "poster_url": url})

        # Trip poster is the last result
        trip_poster_result = poster_results[-1] if poster_results else None
        if isinstance(trip_poster_result, Exception):
            logger.error(f"Trip poster failed: {trip_poster_result}")
            trip_poster_url = ""
        else:
            trip_poster_url = trip_poster_result or ""

        # 5. Generate video using trip poster as input
        video_prompt = f"""
        Cinematic 8-second travel advertisement for "{trip_title}"
        Mood: {trip_visual_theme}
        Style: Smooth drone shots, golden hour, professional travel commercial quality
        """

        video_url = ""
        try:
            # Use trip poster for Image-to-Video, or user upload, or text-only
            video_input = uploaded_file or trip_poster_url or None
            video_url = await self.creative_tools.generate_video(
                video_prompt.strip(),
                image_path=video_input
            )
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            video_url = ""

        logger.info(f"Creative Director complete: {len(daily_posters)} daily posters, 1 trip poster, video={'yes' if video_url else 'no'}")

        return {
            "agent": self.name,
            "trip_poster_url": trip_poster_url,
            "daily_posters": daily_posters,
            "video_url": video_url,
            "status": "success"
        }
