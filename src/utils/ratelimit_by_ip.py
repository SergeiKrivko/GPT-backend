from datetime import datetime, timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import Request, HTTPException, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from src.utils.config import get_ratelimit_settings
from src.utils.dependency import UOWDep
from src.utils.ratelimit_by_ip_model import RatelimitLog
from src.utils.repository import SQLAlchemyRepository
from src.utils.unitofwork import IUnitOfWork


class RatelimitLogRepository(SQLAlchemyRepository):
    model = RatelimitLog

    async def get_count_after(
        self, session: AsyncSession, ip_address: str, timestamp: datetime
    ) -> int:
        stmt = select(func.count()).where(
            self.model.ip_address == ip_address, self.model.timestamp >= timestamp
        )
        result = await session.execute(stmt)
        return result.scalar_one()


@lru_cache
def get_ratelimit_log_repository() -> RatelimitLogRepository:
    return RatelimitLogRepository()


class RatelimiterByIPDep:
    def __init__(
        self,
        ratelimit_log_repository: RatelimitLogRepository,
        ratelimit_requests: int,
        ratelimit_period: int,
    ):
        self.ratelimit_log_repository = ratelimit_log_repository
        self.ratelimit_requests = ratelimit_requests
        self.ratelimit_period = timedelta(seconds=ratelimit_period)

    async def __call__(self, request: Request, uow: IUnitOfWork):
        ip_address = request.client.host
        period_start = datetime.now(tz=None) - self.ratelimit_period

        async with uow:
            request_count = await self.ratelimit_log_repository.get_count_after(
                uow.session, ip_address, period_start
            )

        if request_count >= self.ratelimit_requests:
            raise HTTPException(status_code=429, detail="Too many requests")

        async with uow:
            await self.ratelimit_log_repository.add(
                uow.session, {"ip_address": ip_address}
            )
            await uow.commit()


@lru_cache
def get_ratelimiter() -> RatelimiterByIPDep:
    ratelimit_settings = get_ratelimit_settings()

    return RatelimiterByIPDep(
        ratelimit_log_repository=get_ratelimit_log_repository(),
        ratelimit_requests=ratelimit_settings.requests,
        ratelimit_period=ratelimit_settings.period,
    )


RatelimiterDep = Annotated[RatelimiterByIPDep, Depends(get_ratelimiter)]


async def ratelimit_by_ip(request: Request, uow: UOWDep, ratelimiter: RatelimiterDep):
    await ratelimiter(request, uow)


RatelimitByIpDep = Annotated[None, Depends(ratelimit_by_ip)]
