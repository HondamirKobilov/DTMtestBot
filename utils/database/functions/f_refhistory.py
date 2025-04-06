from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, ReferralHistory


async def create_referral_history(inviter_id: int, invited_id: int, diagnostika_id: int):
    async with AsyncSession(engine) as session:
        try:
            # Avval bunday yozuv mavjud emasligini tekshiramiz
            result = await session.execute(
                select(ReferralHistory).where(
                    ReferralHistory.inviter_id == inviter_id,
                    ReferralHistory.invited_id == invited_id,
                    ReferralHistory.diagnostika_id == diagnostika_id
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                return None  # Allaqachon ushbu kombinatsiya mavjud

            # Yangi yozuvni yaratamiz
            new_entry = ReferralHistory(
                inviter_id=inviter_id,
                invited_id=invited_id,
                diagnostika_id=diagnostika_id
            )
            session.add(new_entry)
            await session.commit()
            await session.refresh(new_entry)
            return new_entry

        except Exception as e:
            print(f"❌ ReferralHistory qo‘shishda xatolik: {e}")
            return None


async def get_referrals_by_user(inviter_id: int, diagnostika_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(ReferralHistory).where(
                ReferralHistory.inviter_id == inviter_id,
                ReferralHistory.diagnostika_id == diagnostika_id
            )
        )
        return result.scalars().all()


async def get_referral_entry(inviter_id: int, invited_id: int, diagnostika_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(ReferralHistory).where(
                ReferralHistory.inviter_id == inviter_id,
                ReferralHistory.invited_id == invited_id,
                ReferralHistory.diagnostika_id == diagnostika_id
            )
        )
        return result.scalar_one_or_none()


async def delete_referral_history(inviter_id: int, invited_id: int, diagnostika_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(ReferralHistory).where(
                ReferralHistory.inviter_id == inviter_id,
                ReferralHistory.invited_id == invited_id,
                ReferralHistory.diagnostika_id == diagnostika_id
            )
        )
        referral = result.scalar_one_or_none()
        if referral:
            await session.delete(referral)
            await session.commit()
            return True
        return False


async def count_referrals(inviter_id: int, diagnostika_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count(ReferralHistory.id)).where(
                ReferralHistory.inviter_id == inviter_id,
                ReferralHistory.diagnostika_id == diagnostika_id
            )
        )
        return result.scalar()
