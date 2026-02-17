"""
Pydantic models for Media Research API
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class MediaLink(BaseModel):
    """
    Represents a media source link with metadata.
    
    Attributes:
        title: The title of the media
        url: Direct URL to the media resource
        size: Size of the media in bytes (optional)
        seeds: Health indicator (higher = better availability)
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Title of the media content"
    )
    url: HttpUrl = Field(
        ...,
        description="Direct URL to the media resource"
    )
    size: Optional[int] = Field(
        None,
        ge=0,
        description="Size in bytes"
    )
    seeds: int = Field(
        ...,
        ge=0,
        description="Health score / seed count"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample Movie (2024)",
                "url": "https://example.com/media/sample.mp4",
                "size": 2147483648,
                "seeds": 150
            }
        }


class SearchResult(BaseModel):
    """
    Container for search results from a provider.
    """
    query: str
    results: list[MediaLink]
    total_results: int
    provider_name: str
