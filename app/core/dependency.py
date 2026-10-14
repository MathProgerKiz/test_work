from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_factory
from app.repositories.index_price import IndexPriceRepository
from app.service.index_price import IndexPriceService


class AppProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_db_session(self) -> AsyncIterator[AsyncSession]:
        async with async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST)
    def provide_index_price_repository(
        self,
        db_session: AsyncSession,
    ) -> IndexPriceRepository:
        return IndexPriceRepository(db_session)

    @provide(scope=Scope.REQUEST)
    def provide_index_price_service(
        self,
        index_price_repository: IndexPriceRepository,
    ) -> IndexPriceService:
        return IndexPriceService(index_price_repository)
