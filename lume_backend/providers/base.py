"""
Abstract Provider Interface
Defines the contract for all media providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from lume_backend.models.schemas import MediaLink


class BaseProvider(ABC):
    """
    Abstract base class for media source providers.
    
    All providers must implement the search method to return
    a list of MediaLink objects matching the query.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        season: Optional[int] = None, 
        episode: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[MediaLink]:
        """
        Search for media matching the query string.
        
        Args:
            query: Search query string (movie title or TV show name)
            season: Optional season number for TV shows
            episode: Optional episode number for TV shows
            limit: Maximum number of results the provider should process
            
        Returns:
            List of MediaLink objects sorted by relevance/quality
            
        Raises:
            ProviderError: If the search operation fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is accessible and functioning.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        pass
    
    def _format_tv_query(self, query: str, season: Optional[int], episode: Optional[int]) -> str:
        """
        Format query with SxxExx notation for TV episodes.
        
        Args:
            query: Base query string
            season: Season number
            episode: Episode number
            
        Returns:
            Formatted query string (e.g., "The Boys S04E01")
        """
        if season is not None and episode is not None:
            return f"{query} S{season:02d}E{episode:02d}"
        elif season is not None:
            return f"{query} S{season:02d}"
        return query


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class ProviderNotFoundError(ProviderError):
    """Raised when no results are found for a query."""
    pass


class ProviderConnectionError(ProviderError):
    """Raised when provider cannot be reached."""
    pass


class ProviderTimeoutError(ProviderError):
    """Raised when provider calls exceed the configured timeout."""
    pass
