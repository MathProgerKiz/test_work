import json
from decimal import Decimal, InvalidOperation

import aiohttp


class DeribitClientError(Exception):
    """The exchange returned an invalid or unsuccessful response."""


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
            try:
                data = await response.json(
                    loads=lambda payload: json.loads(payload, parse_float=Decimal)
                )
            except (json.JSONDecodeError, ValueError) as exc:
                raise DeribitClientError("Не удалось разобрать ответ Deribit") from exc

        if not isinstance(data, dict):
            raise DeribitClientError("Deribit вернул ответ неверного формата")
        if "error" in data:
            raise DeribitClientError(f"Deribit вернул ошибку: {data['error']}")

        try:
            price = Decimal(str(data["result"]["index_price"]))
        except (KeyError, TypeError, InvalidOperation) as exc:
            raise DeribitClientError("Deribit не вернул цену индекса") from exc
        if not price.is_finite() or price <= 0:
            raise DeribitClientError("Deribit вернул некорректную цену")
        return price
