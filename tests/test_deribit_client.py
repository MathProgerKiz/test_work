import asyncio
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.service.deribit_client import DeribitClient


class DeribitClientTests(unittest.TestCase):
    def test_price_is_parsed_without_float_conversion(self):
        response = MagicMock()
        response.json = AsyncMock(
            side_effect=lambda *, loads: loads(
                '{"result":{"index_price":123456789.123456789123}}'
            )
        )
        session = MagicMock()
        session.get.return_value.__aenter__.return_value = response

        price = asyncio.run(DeribitClient(session).get_index_price("btc_usd"))

        self.assertEqual(price, Decimal("123456789.123456789123"))
