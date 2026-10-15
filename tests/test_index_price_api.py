import os
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


with patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql+psycopg://user:pass@localhost/test",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
    },
):
    from app.main import app
    from app.service.index_price import IndexPriceService


class IndexPriceApiTests(unittest.TestCase):
    def test_list_returns_all_by_default_and_validates_pagination(self):
        with patch.object(
            IndexPriceService,
            "get_list_index_prices",
            new_callable=AsyncMock,
            return_value=[],
        ) as get_list:
            with TestClient(app) as client:
                response = client.get("/api/v1/index-prices?ticker=btc_usd")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), [])
                get_list.assert_awaited_with(ticker="btc_usd", limit=None, offset=0)

                response = client.get(
                    "/api/v1/index-prices?ticker=btc_usd&limit=25&offset=5"
                )
                self.assertEqual(response.status_code, 200)
                get_list.assert_awaited_with(ticker="btc_usd", limit=25, offset=5)

                for query in ("limit=0", "limit=1001", "offset=-1"):
                    response = client.get(f"/api/v1/index-prices?ticker=btc_usd&{query}")
                    self.assertEqual(response.status_code, 422, query)

                self.assertEqual(get_list.await_count, 2)
