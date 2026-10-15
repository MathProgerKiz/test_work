from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from celery.exceptions import Retry

from app import tasks
from app.service.deribit_client import DeribitClientError


@pytest.mark.asyncio
async def test_engine_is_disposed_after_success_and_database_error():
    engines = [MagicMock(), MagicMock()]
    for engine in engines:
        engine.dispose = AsyncMock()

    session_factory = MagicMock()
    session_factory.begin.return_value.__aenter__.return_value = MagicMock()
    repository = MagicMock()
    repository.create_index_price = AsyncMock(
        side_effect=[None, None, RuntimeError("database write failed")]
    )
    deribit = MagicMock()
    deribit.get_index_price = AsyncMock(return_value=Decimal("1.00"))

    with (
        patch("app.tasks.aiohttp.ClientSession"),
        patch("app.tasks.DeribitClient", return_value=deribit),
        patch("app.tasks.IndexPriceRepository", return_value=repository),
        patch("app.tasks.create_async_engine", side_effect=engines) as create_engine,
        patch("app.tasks.async_sessionmaker", return_value=session_factory) as maker,
    ):
        await tasks.fetch_and_save_prices(125)
        with pytest.raises(RuntimeError, match="database write failed"):
            await tasks.fetch_and_save_prices(130)

    assert create_engine.call_count == 2
    assert maker.call_args_list == [
        call(engines[0], expire_on_commit=False),
        call(engines[1], expire_on_commit=False),
    ]
    engines[0].dispose.assert_awaited_once()
    engines[1].dispose.assert_awaited_once()
    assert [
        item.kwargs["timestamp"]
        for item in repository.create_index_price.call_args_list
    ] == [120, 120, 120]


@pytest.mark.parametrize(
    "error",
    [
        DeribitClientError("temporary exchange error"),
        tasks.SQLAlchemyError("temporary database error"),
    ],
)
def test_retry_preserves_original_collection_minute(error):
    retry_exception = Retry("retry requested")
    with (
        patch(
            "app.tasks.fetch_and_save_prices",
            new_callable=AsyncMock,
            side_effect=error,
        ),
        patch("app.tasks.time.time", return_value=125),
        patch.object(
            tasks.fetch_and_save_prices_task,
            "retry",
            side_effect=retry_exception,
        ) as retry,
        pytest.raises(Retry),
    ):
        tasks.fetch_and_save_prices_task.run()

    retry.assert_called_once()
    assert retry.call_args.kwargs["kwargs"] == {"timestamp": 120}
    assert retry.call_args.kwargs["max_retries"] == 3
