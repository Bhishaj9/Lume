"""
Mock Provider Implementation
For testing and development purposes.
"""
import random
from typing import List, Optional
from providers.base import BaseProvider, ProviderNotFoundError
from models.schemas import MediaLink


class MockProvider(BaseProvider):
    """
    Mock provider that returns hardcoded sample data.
    Useful for testing the API without external dependencies.
    """
    
    def __init__(self):
        super().__init__(name="MockProvider")
        self._mock_database = [
            # Movies
            {
                "title": "Inception (2010) 1080p BluRay",
                "url": "https://mock-cdn.example.com/movies/inception-2010.mkv",
                "size": 8542781952,
                "seeds": 2450
            },
            {
                "title": "The Dark Knight (2008) 1080p",
                "url": "https://mock-cdn.example.com/movies/dark-knight-2008.mkv",
                "size": 9126805504,
                "seeds": 1890
            },
            {
                "title": "Interstellar (2014) 4K HDR",
                "url": "https://mock-cdn.example.com/movies/interstellar-2014.mkv",
                "size": 23622320128,
                "seeds": 920
            },
            # TV Shows - The Boys
            {
                "title": "The Boys S04E01 1080p WEB-DL",
                "url": "https://mock-cdn.example.com/tv/the-boys/s04e01.mkv",
                "size": 2147483648,
                "seeds": 1500
            },
            {
                "title": "The Boys S04E02 1080p WEB-DL",
                "url": "https://mock-cdn.example.com/tv/the-boys/s04e02.mkv",
                "size": 2084567130,
                "seeds": 1400
            },
            {
                "title": "The Boys S03E01 1080p WEB-DL",
                "url": "https://mock-cdn.example.com/tv/the-boys/s03e01.mkv",
                "size": 1984567130,
                "seeds": 1200
            },
            # TV Shows - Breaking Bad
            {
                "title": "Breaking Bad S01E01 1080p BluRay",
                "url": "https://mock-cdn.example.com/tv/breaking-bad/s01e01.mkv",
                "size": 1800000000,
                "seeds": 3000
            },
            {
                "title": "Breaking Bad S01E02 1080p BluRay",
                "url": "https://mock-cdn.example.com/tv/breaking-bad/s01e02.mkv",
                "size": 1750000000,
                "seeds": 2800
            },
            # TV Shows - Stranger Things
            {
                "title": "Stranger Things S01E01 1080p NF WEB-DL",
                "url": "https://mock-cdn.example.com/tv/stranger-things/s01e01.mkv",
                "size": 2200000000,
                "seeds": 2500
            },
        ]
    
    async def search(
        self, 
        query: str, 
        season: Optional[int] = None, 
        episode: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[MediaLink]:
        """
        Search mock database for matching titles.
        
        For TV shows with season/episode, formats query as "Title SxxExx"
        and filters results to match that specific episode.
        """
        # Format query with SxxExx if season and episode provided
        formatted_query = self._format_tv_query(query, season, episode)
        query_lower = formatted_query.lower().strip()
        
        print(f"🔍 Searching for: {formatted_query}")
        
        # Special case for testing empty results
        if query_lower == "empty":
            raise ProviderNotFoundError(f"No results found for: {query}")
        
        # Return all mock data or filter by query
        if query_lower == "all":
            filtered = self._mock_database
        else:
            # For TV episodes with SxxExx format, be more specific
            if season is not None and episode is not None:
                # Strict matching for TV episodes - must contain SxxExx
                filtered = [
                    item for item in self._mock_database
                    if query_lower in item["title"].lower() 
                    and f"s{season:02d}e{episode:02d}" in item["title"].lower()
                ]
            elif season is not None:
                # Match season only
                filtered = [
                    item for item in self._mock_database
                    if query_lower in item["title"].lower()
                    and f"s{season:02d}" in item["title"].lower()
                ]
            else:
                # Regular movie/show search
                filtered = [
                    item for item in self._mock_database
                    if query_lower in item["title"].lower()
                ]
        
        if not filtered:
            raise ProviderNotFoundError(f"No results found for: {formatted_query}")
        
        # Sort by seeds (highest first)
        sorted_results = sorted(
            filtered,
            key=lambda x: x["seeds"],
            reverse=True
        )
        
        return [MediaLink(**item) for item in sorted_results]
    
    async def health_check(self) -> bool:
        """Mock provider is always healthy."""
        return True


class RandomMockProvider(BaseProvider):
    """
    Generates random mock data for load testing.
    """
    
    def __init__(self):
        super().__init__(name="RandomMockProvider")
    
    async def search(
        self, 
        query: str, 
        season: Optional[int] = None, 
        episode: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[MediaLink]:
        """Generate random results."""
        formatted_query = self._format_tv_query(query, season, episode)
        
        num_results = random.randint(1, 10)
        results = []
        
        for i in range(num_results):
            results.append(MediaLink(
                title=f"{formatted_query} - Random Result {i+1}",
                url=f"https://mock.example.com/{formatted_query.replace(' ', '-')}-{i}",
                size=random.randint(1000000000, 25000000000),
                seeds=random.randint(10, 5000)
            ))
        
        return sorted(results, key=lambda x: x.seeds, reverse=True)
    
    async def health_check(self) -> bool:
        return True
