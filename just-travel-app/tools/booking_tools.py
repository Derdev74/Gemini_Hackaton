"""
Booking Tools
=============

This module provides integration with Booking.com (via RapidAPI) for
accommodation searching.
"""

import os
import logging
import requests
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class BookingTools:
    """
    Tool class for hotel and accommodation search via Booking.com API.
    """

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.host = "booking-com.p.rapidapi.com"
        self._connected = bool(self.api_key and "placeholder" not in self.api_key)

    def search_hotels(
        self,
        location: str,
        checkin_date: str,
        checkout_date: str,
        adults: int = 2,
        rooms: int = 1,
        currency: str = "USD"
    ) -> List[Dict]:
        """
        Search for hotels in a location.
        Note: Real API requires precise location_id or latch/long. 
        For hackathon simplicity, we might simulate the location lookup or focus on mocking 
        until we handle the 2-step process (Location Search -> Hotel Search).
        """
        if not self._connected:
            return self._get_mock_hotels(location)

        # In a full specific implementation, we would first call locations/search
        # then hotels/search. For this level of detail, we structure the call 
        # but return mocks unless the key is extremely active/configured.
        
        # This is a placeholder for the actual robust implementation
        logger.info(f"Searching hotels in {location} via API (Not fully implemented without Location ID logic)")
        return self._get_mock_hotels(location)

    def _get_mock_hotels(self, location: str) -> List[Dict]:
        """Return mock hotel data."""
        return [
            {
                "name": f"Grand Hotel {location}",
                "price": "$200/night",
                "rating": 4.5,
                "address": "City Center",
                "link": "https://booking.com/mock1"
            },
            {
                "name": f"{location} Budget Inn",
                "price": "$85/night",
                "rating": 3.8,
                "address": "Near Station",
                "link": "https://booking.com/mock2"
            },
            {
                "name": "Luxury Resort & Spa",
                "price": "$450/night",
                "rating": 4.9,
                "address": "Seaside",
                "link": "https://booking.com/mock3"
            }
        ]
