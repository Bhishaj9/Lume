import asyncio
from types import SimpleNamespace

from fastapi.testclient import TestClient

from lume_backend.main import create_application
from lume_backend.models.schemas import MediaLink
from lume_backend.providers.base import BaseProvider, ProviderTimeoutError
from lume_backend.providers.p2p_provider import P2PProvider
from lume_backend.routers.media import get_provider


class TimeoutProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("TimeoutProvider")

    async def search(self, query, season=None, episode=None, limit=None):
        raise ProviderTimeoutError("upstream timed out")

    async def health_check(self) -> bool:
        return True


class DeadResultsProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("DeadResultsProvider")

    async def search(self, query, season=None, episode=None, limit=None):
        return [
            MediaLink(title=f"Dead {i}", url="https://example.com/dead", size=1, seeds=0)
            for i in range(10)
        ]

    async def health_check(self) -> bool:
        return True


class ManyResultsProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("ManyResultsProvider")

    async def search(self, query, season=None, episode=None, limit=None):
        cap = limit if limit is not None else 100
        return [
            MediaLink(
                title=f"Live {i}",
                url="https://example.com/live",
                size=1000 + i,
                seeds=50 - i,
            )
            for i in range(cap)
        ]

    async def health_check(self) -> bool:
        return True


def _client_for(provider):
    app = create_application()
    app.dependency_overrides[get_provider] = lambda: provider
    return TestClient(app)


def test_timeout_is_mapped_to_504():
    client = _client_for(TimeoutProvider())

    response = client.get("/resolve/search/inception")

    assert response.status_code == 504
    assert response.json()["detail"]["error"] == "PROVIDER_TIMEOUT"


def test_dead_results_are_filtered_out():
    client = _client_for(DeadResultsProvider())

    response = client.get("/resolve/search/inception")

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == []
    assert payload["total_results"] == 0


def test_limit_is_enforced_and_validated():
    client = _client_for(ManyResultsProvider())

    ok_response = client.get("/resolve/search/inception?limit=25")
    assert ok_response.status_code == 200
    assert len(ok_response.json()["results"]) == 25

    bad_response = client.get("/resolve/search/inception?limit=100")
    assert bad_response.status_code == 422


def test_p2p_provider_filters_dead_results_and_respects_limit(monkeypatch):
    class FakePirateBayAPI:
        @staticmethod
        def Search(_query):
            return [
                SimpleNamespace(id=1, name="dead", size=1, seeds=0),
                SimpleNamespace(id=2, name="live-1", size=2, seeds=10),
                SimpleNamespace(id=3, name="live-2", size=3, seeds=9),
                SimpleNamespace(id=4, name="live-3", size=4, seeds=8),
            ]

        @staticmethod
        def Download(item_id):
            return f"https://example.com/{item_id}"

    monkeypatch.setattr("lume_backend.providers.p2p_provider.PirateBayAPI", FakePirateBayAPI)
    provider = P2PProvider()

    results = asyncio.run(provider.search("query", limit=2))

    assert len(results) == 2
    assert all(item.seeds > 0 for item in results)


def test_p2p_provider_timeout_raises_provider_timeout(monkeypatch):
    def slow_search(_query):
        import time

        time.sleep(16)
        return []

    class FakePirateBayAPI:
        @staticmethod
        def Search(query):
            return slow_search(query)

        @staticmethod
        def Download(_item_id):
            return "https://example.com/file"

    monkeypatch.setattr("lume_backend.providers.p2p_provider.PirateBayAPI", FakePirateBayAPI)
    provider = P2PProvider()

    try:
        asyncio.run(provider.search("query", limit=1))
        assert False, "expected ProviderTimeoutError"
    except ProviderTimeoutError:
        assert True
