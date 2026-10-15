from decimal import Decimal


class IndexPriceService:

    def __init__(self, index_price_repository):
        self.index_price_repository = index_price_repository

    async def get_last_index_price(self, ticker: str):
        return await self.index_price_repository.get_last_index_price(ticker)

    async def create_index_price(self, ticker: str, price: Decimal, timestamp: int):
        return await self.index_price_repository.create_index_price(
            ticker,
            price,
            timestamp,
        )

    async def get_list_index_prices(
        self,
        ticker: str,
        limit: int = 10,
        offset: int = 0,
    ):
        return await self.index_price_repository.get_list_index_prices(
            ticker,
            limit,
            offset,
        )

    async def get_index_price_by_timestamp(self, ticker: str, timestamp: int):
        return await self.index_price_repository.get_index_price_by_timestamp(
            ticker,
            timestamp,
        )
