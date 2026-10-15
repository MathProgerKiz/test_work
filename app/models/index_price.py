from decimal import Decimal

from sqlalchemy import BigInteger, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class IndexPrice(Base):
    __tablename__ = "index_prices"

    __table_args__ = (
        UniqueConstraint(
            "ticker", "timestamp", name="uq_index_prices_ticker_timestamp"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
