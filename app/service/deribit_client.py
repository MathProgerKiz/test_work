import json
from decimal import Decimal

import aiohttp


class DeribitClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = "https://www.deribit.com/api/v2"

    async def get_index_price(self, index_name: str) -> Decimal:
        url = f"{self.base_url}/public/get_index_price"

        async with self.session.get(
            url,
            params={"index_name": index_name},
        ) as response:
            response.raise_for_status()
            data = await response.json(
                loads=lambda payload: json.loads(payload, parse_float=Decimal)
            )

        if "error" in data:
            raise RuntimeError(f"Deribit вернул ошибку: {data['error']}")

        price = Decimal(str(data["result"]["index_price"]))
        if not price.is_finite() or price <= 0:
            raise ValueError("Deribit вернул некорректную цену")
        return price
