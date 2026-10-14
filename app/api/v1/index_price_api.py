from typing import Literal

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.schemas.index_price import IndexPriceCreate, IndexPriceRead
from app.service.index_price import IndexPriceService


router = APIRouter(
    prefix="/index-prices",
    tags=["Index prices"],
)


@router.get(
    "/{ticker}/last",
    response_model=IndexPriceRead | None,
)
@inject
async def get_last_index_price(
    ticker: Literal["btc_usd", "eth_usd"],
    service: FromDishka[IndexPriceService],
):
    return await service.get_last_index_price(ticker)

@router.post(
    "/{ticker}",
    response_model=IndexPriceRead,
)
@inject
async def create_index_price(
    ticker: Literal["btc_usd", "eth_usd"],
    index_price_create: IndexPriceCreate,
    service: FromDishka[IndexPriceService],
):
    return await service.create_index_price(
        ticker=ticker,
        price=index_price_create.price,
        timestamp=index_price_create.timestamp,
    )

@router.get(
    "/{ticker}",
    response_model=list[IndexPriceRead],
)
@inject
async def get_list_index_prices(
    ticker: Literal["btc_usd", "eth_usd"],
    service: FromDishka[IndexPriceService],
    limit: int = 10,
    offset: int = 0
):
    return await service.get_list_index_prices(
        ticker=ticker,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{ticker}/{timestamp}",
    response_model=IndexPriceRead | None,
)
@inject
async def get_index_price_by_timestamp(
    ticker: Literal["btc_usd", "eth_usd"],
    timestamp: int,
    service: FromDishka[IndexPriceService],
):
    return await service.get_index_price_by_timestamp(
        ticker=ticker,
        timestamp=timestamp,
    )

