from unittest.mock import AsyncMock

import pytest

from app.service.index_price import IndexPriceService


@pytest.mark.asyncio
async def test_timestamp_is_normalized_to_minute():
    repository = AsyncMock()
    repository.get_index_price_by_timestamp.return_value = None
    service = IndexPriceService(repository)

    await service.get_index_price_by_timestamp("btc_usd", 179)

    repository.get_index_price_by_timestamp.assert_awaited_once_with("btc_usd", 120)
