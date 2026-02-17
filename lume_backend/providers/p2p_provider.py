"""P2P provider implementation backed by PirateBayAPI."""
import asyncio
from typing import List, Optional

from fastapi.concurrency import run_in_threadpool

try:
    from PirateBayAPI import PirateBayAPI
except ImportError:  # pragma: no cover - optional dependency in local/dev environments
    PirateBayAPI = None

from lume_backend.models.schemas import MediaLink
from lume_backend.providers.base import BaseProvider, ProviderConnectionError, ProviderTimeoutError


PROVIDER_TIMEOUT_SECONDS = 15


class P2PProvider(BaseProvider):
    """Provider that resolves media links from P2P index results."""

    def __init__(self) -> None:
        super().__init__(name="P2PProvider")

    async def search(
        self,
        query: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[MediaLink]:
        """Search PirateBayAPI and return ranked ``MediaLink`` objects."""
        formatted_query = self._format_tv_query(query, season, episode)
        effective_limit = max(1, limit or 10)

        if PirateBayAPI is None:
            raise ProviderConnectionError("PirateBayAPI dependency is not installed")

        try:
            results = await asyncio.wait_for(
                run_in_threadpool(PirateBayAPI.Search, formatted_query),
                timeout=PROVIDER_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            raise ProviderTimeoutError("P2P provider search timed out") from exc
        except Exception as exc:  # noqa: BLE001
            raise ProviderConnectionError("Failed to query P2P provider") from exc

        if not results:
            return []

        sorted_results = sorted(
            results,
            key=lambda item: int(getattr(item, "seeds", 0) or 0),
            reverse=True,
        )

        live_results = [item for item in sorted_results if int(getattr(item, "seeds", 0) or 0) > 0]

        media_links: List[MediaLink] = []
        for item in live_results[:effective_limit]:
            try:
                magnet_url = await asyncio.wait_for(
                    run_in_threadpool(PirateBayAPI.Download, item.id),
                    timeout=PROVIDER_TIMEOUT_SECONDS,
                )
                media_links.append(
                    MediaLink(
                        title=str(getattr(item, "name", formatted_query)),
                        url=magnet_url,
                        size=int(getattr(item, "size", 0) or 0),
                        seeds=int(getattr(item, "seeds", 0) or 0),
                    )
                )
            except asyncio.TimeoutError:
                continue
            except Exception:
                continue

        return media_links

    async def health_check(self) -> bool:
        """Basic provider health-check by issuing a lightweight search."""
        if PirateBayAPI is None:
            return False

        try:
            await asyncio.wait_for(
                run_in_threadpool(PirateBayAPI.Search, "test"),
                timeout=PROVIDER_TIMEOUT_SECONDS,
            )
            return True
        except Exception:
            return False
