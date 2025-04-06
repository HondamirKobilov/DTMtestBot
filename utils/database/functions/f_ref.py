from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from utils.database.models import engine, Base, ReferralCount

async def create_referral_table():
    async with engine.begin() as conn:
        await conn.run_sync(ReferralCount.__table__.create, checkfirst=True)
        print("✅ Referral jadvali yaratildi yoki mavjud edi.")

async def get_referral_count():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(ReferralCount))
        ref = result.scalar_one_or_none()
        if not ref:
            ref = ReferralCount(count=0)
            session.add(ref)
            await session.commit()
            await session.refresh(ref)
        return ref

async def increment_referral_count():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(ReferralCount))
        ref = result.scalar_one_or_none()

        if not ref:
            ref = ReferralCount(count=1)
            session.add(ref)
        else:
            ref.count += 1

        await session.commit()

async def set_referral_count(value: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(ReferralCount))
        ref = result.scalar_one_or_none()

        if not ref:
            ref = ReferralCount(count=value)
            session.add(ref)
        else:
            ref.count = value

        await session.commit()

async def view_referral_count():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(ReferralCount))
        ref = result.scalar_one_or_none()
        return ref.count if ref else 0
