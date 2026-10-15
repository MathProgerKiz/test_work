from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.index_price import IndexPrice


class IndexPriceRepository:
    def __init__(self, db):
        self.db = db

    async def get_last_index_price(self, ticker: str):
        result = await self.db.scalars(
            select(IndexPrice)
            .where(IndexPrice.ticker == ticker)
            .order_by(IndexPrice.timestamp.desc())
            .limit(1)
        )
        return result.first()

    async def create_index_price(self, ticker: str, price: Decimal, timestamp: int):
        statement = (
            insert(IndexPrice)
            .values(ticker=ticker, price=price, timestamp=timestamp)
            .on_conflict_do_nothing(constraint="uq_index_prices_ticker_timestamp")
            .returning(IndexPrice)
        )
        result = await self.db.scalars(statement)
        return result.first() or await self.get_index_price_by_timestamp(
            ticker, timestamp
        )

    async def get_list_index_prices(
        self, ticker: str, limit: int | None = None, offset: int = 0
    ):
        statement = (
            select(IndexPrice)
            .where(IndexPrice.ticker == ticker)
            .order_by(IndexPrice.timestamp.desc(), IndexPrice.id.desc())
        )
        if offset:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)

        result = await self.db.scalars(statement)
        return result.all()

    async def get_index_price_by_timestamp(self, ticker: str, timestamp: int):
        result = await self.db.scalars(
            select(IndexPrice).where(
                IndexPrice.ticker == ticker, IndexPrice.timestamp == timestamp
            )
        )
        return result.first()
