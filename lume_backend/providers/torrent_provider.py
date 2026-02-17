"""Torrent provider implementation backed by PirateBayAPI."""
from typing import List, Optional

from PirateBayAPI import PirateBayAPI
from fastapi.concurrency import run_in_threadpool

from lume_backend.models.schemas import MediaLink
from lume_backend.providers.base import BaseProvider, ProviderConnectionError


class TorrentProvider(BaseProvider):
    """Provider that resolves media links from torrent index results."""

    def __init__(self) -> None:
        super().__init__(name="TorrentProvider")

    async def search(
        self,
        query: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
    ) -> List[MediaLink]:
        """Search PirateBayAPI and return ranked ``MediaLink`` objects."""
        formatted_query = self._format_tv_query(query, season, episode)

        try:
            results = await run_in_threadpool(PirateBayAPI.Search, formatted_query)
        except Exception as exc:  # noqa: BLE001
            raise ProviderConnectionError("Failed to query torrent provider") from exc

        if not results:
            return []

        sorted_results = sorted(
            results,
            key=lambda item: int(getattr(item, "seeds", 0) or 0),
            reverse=True,
        )

        media_links: List[MediaLink] = []
        for item in sorted_results:
            try:
                magnet_url = await run_in_threadpool(PirateBayAPI.Download, item.id)
                media_links.append(
                    MediaLink(
                        title=str(getattr(item, "name", formatted_query)),
                        url=magnet_url,
                        size=int(getattr(item, "size", 0) or 0),
                        seeds=int(getattr(item, "seeds", 0) or 0),
                    )
                )
            except Exception:
                continue

        return media_links

    async def health_check(self) -> bool:
        """Basic provider health-check by issuing a lightweight search."""
        try:
            await run_in_threadpool(PirateBayAPI.Search, "test")
            return True
        except Exception:
            return False
