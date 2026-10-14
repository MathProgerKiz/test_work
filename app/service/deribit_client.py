import aiohttp


class DeribitClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = "https://www.deribit.com/api/v2"

    async def get_index_price(self, index_name: str) -> float:
        url = f"{self.base_url}/public/get_index_price"

        async with self.session.get(
            url,
            params={"index_name": index_name},
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if "error" in data:
            raise RuntimeError(f"Deribit вернул ошибку: {data['error']}")

        return data["result"]["index_price"]