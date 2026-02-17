"""
FastAPI Router for Media Resolution
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from lume_backend.models.schemas import MediaLink, SearchResult
from lume_backend.providers.base import (
    BaseProvider,
    ProviderConnectionError,
    ProviderNotFoundError,
    ProviderTimeoutError,
)
from lume_backend.providers.mock_provider import MockProvider


# Create router
router = APIRouter(
    prefix="/resolve",
    tags=["media-resolution"],
    responses={
        404: {"description": "No results found"},
        422: {"description": "Invalid TV season/episode parameters"},
        503: {"description": "Provider unavailable"},
        504: {"description": "Provider timeout"},
    },
)


def get_provider() -> BaseProvider:
    """
    Dependency injection for the media provider.

    Easily swap providers by changing this function:
    - MockProvider (for testing)
    - TMDBProvider (for metadata)
    - CustomProvider (your implementation)
    """
    return MockProvider()


def _map_provider_exception(exc: Exception) -> HTTPException:
    """Map known provider exceptions to API-level HTTP exceptions."""
    if isinstance(exc, ProviderNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": str(exc),
            },
        )
    if isinstance(exc, ProviderConnectionError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "PROVIDER_UNAVAILABLE",
                "message": str(exc),
            },
        )
    if isinstance(exc, ProviderTimeoutError):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": "PROVIDER_TIMEOUT",
                "message": str(exc),
            },
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error: {str(exc)}",
        },
    )




def _filter_live_results(results: list[MediaLink]) -> list[MediaLink]:
    """Remove dead results (zero or negative seeds)."""
    return [result for result in results if result.seeds > 0]

def _format_tv_query(query: str, season: Optional[int], episode: Optional[int]) -> str:
    """Format a media query for TV searches and validate season/episode bounds."""
    if season is not None and season <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "INVALID_SEASON", "message": "season must be greater than 0"},
        )
    if episode is not None and episode <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "INVALID_EPISODE", "message": "episode must be greater than 0"},
        )

    if season is not None and episode is not None:
        return f"{query} S{season:02d}E{episode:02d}"
    if season is not None:
        return f"{query} S{season:02d}"
    return query


@router.get(
    "/{query}",
    response_model=MediaLink,
    summary="Resolve top media result",
    description="Search for media and return the highest-quality result. For TV episodes, use season and episode parameters.",
)
async def resolve_media(
    query: str,
    season: Optional[int] = Query(None, description="Season number for TV shows (e.g., 4)"),
    episode: Optional[int] = Query(None, description="Episode number for TV shows (e.g., 1)"),
    provider: BaseProvider = Depends(get_provider),
) -> MediaLink:
    """
    Resolve a media query to the best available source.

    - **query**: Search string (movie title, show name, etc.)
    - **season**: Optional season number for TV shows
    - **episode**: Optional episode number for TV shows
    - Returns the single best result sorted by seed count

    For TV episodes, the search will be formatted as: "{title} S{season:02d}E{episode:02d}"
    Example: query="The Boys", season=4, episode=1 → searches for "The Boys S04E01"

    Use query='all' to get all mock results.
    Use query='empty' to test 404 handling.
    """
    formatted_query = _format_tv_query(query, season, episode)
    try:
        results = await provider.search(query, season=season, episode=episode, limit=1)
        live_results = _filter_live_results(results)

        if not live_results:
            raise ProviderNotFoundError(f"No live results found for: {formatted_query}")

        # Return top live result (already sorted by provider)
        return live_results[0]
    except HTTPException:
        raise
    except Exception as exc:
        mapped_exception = _map_provider_exception(exc)
        mapped_exception.detail["query"] = query
        mapped_exception.detail["season"] = season
        mapped_exception.detail["episode"] = episode
        if mapped_exception.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            mapped_exception.detail["provider"] = provider.name
        raise mapped_exception


@router.get(
    "/search/{query}",
    response_model=SearchResult,
    summary="Search all media results",
    description="Search for media and return all matching results. Supports TV episode filtering.",
)
async def search_media(
    query: str,
    season: Optional[int] = Query(None, description="Season number for TV shows"),
    episode: Optional[int] = Query(None, description="Episode number for TV shows"),
    limit: int = Query(10, ge=1, le=25, description="Maximum number of results (1-25)"),
    provider: BaseProvider = Depends(get_provider),
) -> SearchResult:
    """
    Search for media and return all results.

    - **query**: Search string
    - **season**: Optional season number for TV shows
    - **episode**: Optional episode number for TV shows
    - **limit**: Maximum number of results (default: 10)

    When season and episode are provided, filters results to match the specific episode.
    """
    _format_tv_query(query, season, episode)
    try:
        results = await provider.search(query, season=season, episode=episode, limit=limit)
        live_results = _filter_live_results(results)

        # Apply strict limit on live results
        limited_results = live_results[:limit]

        return SearchResult(
            query=query,
            results=limited_results,
            total_results=len(live_results),
            provider_name=provider.name,
        )
    except HTTPException:
        raise
    except Exception as exc:
        mapped_exception = _map_provider_exception(exc)
        mapped_exception.detail["query"] = query
        mapped_exception.detail["season"] = season
        mapped_exception.detail["episode"] = episode
        if mapped_exception.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            mapped_exception.detail["provider"] = provider.name
        raise mapped_exception


@router.get(
    "/health/provider",
    summary="Check provider health",
    description="Verify that the media provider is accessible",
)
async def check_provider_health(provider: BaseProvider = Depends(get_provider)) -> dict:
    """Check if the provider is healthy."""
    is_healthy = await provider.health_check()

    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "provider": provider.name},
        )

    return {"status": "healthy", "provider": provider.name}
