from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.main import app
from app.service.index_price import IndexPriceService


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.mark.asyncio
async def test_api_documentation_is_available(client):
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"

    response = await client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_list_returns_all_by_default_and_validates_pagination(client):
    with patch.object(
        IndexPriceService,
        "get_list_index_prices",
        new_callable=AsyncMock,
        return_value=[],
    ) as get_list:
        response = await client.get("/api/v1/index-prices?ticker=btc_usd")
        assert response.status_code == 200
        assert response.json() == []
        get_list.assert_awaited_with(ticker="btc_usd", limit=None, offset=0)

        response = await client.get(
            "/api/v1/index-prices?ticker=btc_usd&limit=25&offset=5"
        )
        assert response.status_code == 200
        get_list.assert_awaited_with(ticker="btc_usd", limit=25, offset=5)

        for query in ("limit=0", "limit=1001", "offset=-1"):
            response = await client.get(f"/api/v1/index-prices?ticker=btc_usd&{query}")
            assert response.status_code == 422, query

        assert get_list.await_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/index-prices",
        "/api/v1/index-prices/last",
        "/api/v1/index-prices/by-timestamp?timestamp=125",
    ],
)
async def test_ticker_is_required_for_every_endpoint(client, path):
    response = await client.get(path)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_last_and_timestamp_endpoints(client):
    price = {
        "id": 1,
        "ticker": "btc_usd",
        "price": "123.45",
        "timestamp": 120,
    }
    with (
        patch.object(
            IndexPriceService,
            "get_last_index_price",
            new_callable=AsyncMock,
            return_value=price,
        ) as get_last,
        patch.object(
            IndexPriceService,
            "get_index_price_by_timestamp",
            new_callable=AsyncMock,
            return_value=price,
        ) as get_by_timestamp,
    ):
        response = await client.get("/api/v1/index-prices/last?ticker=btc_usd")
        assert response.status_code == 200
        get_last.assert_awaited_once_with("btc_usd")

        response = await client.get(
            "/api/v1/index-prices/by-timestamp?ticker=btc_usd&timestamp=125"
        )
        assert response.status_code == 200
        get_by_timestamp.assert_awaited_once_with(ticker="btc_usd", timestamp=125)
