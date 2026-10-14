

from sqlalchemy import select

from app.models.index_price import IndexPrice


class IndexPriceRepository:
    def __init__(self, db):
        self.db = db

    async def get_last_index_price(self, ticker: str):
        result = await self.db.scalars(select(IndexPrice).where(IndexPrice.ticker == ticker).order_by(IndexPrice.timestamp.desc()).limit(1))
        return result.first()

    async def create_index_price(self, ticker: str, price: float, timestamp: int):
        index_price = IndexPrice(ticker=ticker, price=price, timestamp=timestamp)
        self.db.add(index_price)
        await self.db.commit()
        await self.db.refresh(index_price)
        return index_price

    async def get_list_index_prices(self, ticker: str, limit: int = 10, offset: int = 0):
        result = await self.db.scalars(
            select(IndexPrice).where(IndexPrice.ticker == ticker).order_by(IndexPrice.timestamp.desc()).limit(limit).offset(offset)
        )
        return result.all()

    async def get_index_price_by_timestamp(self, ticker: str, timestamp: int):
        result = await self.db.scalars(
            select(IndexPrice).where(IndexPrice.ticker == ticker, IndexPrice.timestamp == timestamp)
        )
        return result.first()
