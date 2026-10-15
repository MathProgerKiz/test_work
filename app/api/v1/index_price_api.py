from typing import Annotated, Literal

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query

from app.schemas.index_price import IndexPriceRead
from app.service.index_price import IndexPriceService

router = APIRouter(
    prefix="/index-prices",
    tags=["Index prices"],
)


@router.get(
    "/last",
    response_model=IndexPriceRead | None,
)
@inject
async def get_last_index_price(
    ticker: Literal["btc_usd", "eth_usd"],
    service: FromDishka[IndexPriceService],
):
    return await service.get_last_index_price(ticker)


@router.get(
    "",
    response_model=list[IndexPriceRead],
)
@inject
async def get_list_index_prices(
    ticker: Literal["btc_usd", "eth_usd"],
    service: FromDishka[IndexPriceService],
    limit: Annotated[int | None, Query(ge=1, le=1000)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.get_list_index_prices(
        ticker=ticker,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/by-timestamp",
    response_model=IndexPriceRead | None,
)
@inject
async def get_index_price_by_timestamp(
    ticker: Literal["btc_usd", "eth_usd"],
    timestamp: Annotated[
        int,
        Query(
            ge=0,
            description=("Любой UNIX timestamp внутри искомой минуты (UTC)"),
        ),
    ],
    service: FromDishka[IndexPriceService],
):
    return await service.get_index_price_by_timestamp(
        ticker=ticker,
        timestamp=timestamp,
    )
