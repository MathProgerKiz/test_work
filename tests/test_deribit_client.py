from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.service.deribit_client import DeribitClient, DeribitClientError


@pytest.mark.asyncio
async def test_price_is_parsed_without_float_conversion():
    response = MagicMock()
    response.json = AsyncMock(
        side_effect=lambda *, loads: loads(
            '{"result":{"index_price":123456789.123456789123}}'
        )
    )
    session = MagicMock()
    session.get.return_value.__aenter__.return_value = response

    price = await DeribitClient(session).get_index_price("btc_usd")

    assert price == Decimal("123456789.123456789123")


@pytest.mark.asyncio
async def test_exchange_error_raises_retryable_client_error():
    response = MagicMock()
    response.json = AsyncMock(
        return_value={"error": {"code": 10028, "message": "too_many_requests"}}
    )
    session = MagicMock()
    session.get.return_value.__aenter__.return_value = response

    with pytest.raises(DeribitClientError, match="too_many_requests"):
        await DeribitClient(session).get_index_price("btc_usd")
