from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, User


async def create_user(user_id, username, is_premium=False, referral_count=None):
    async with AsyncSession(engine) as session:
        try:
            new_user = User(
                user_id=user_id,
                username=username,
                is_premium=is_premium,
                referral_count=referral_count
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except:
            pass


async def update_user(user_id: int, **kwargs):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            await session.commit()
            return user
        else:
            return False


async def select_user(user_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()


async def select_user_language(user_id: int):
    async with AsyncSession(engine) as session:
        if not user_id:
            return None
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is not None:
            return user.language
        return user


async def get_all_users():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.is_blocked == False))
        return [user.user_id for user in result.scalars().all()]


async def get_all_users_posts(is_phone=False):
    async with AsyncSession(engine) as session:
        if not is_phone:
            result = await session.execute(select(User).where(User.is_blocked == False))
        else:
            result = await session.execute(select(User).where(User.is_blocked == False, User.phone.is_(None)))

        return [(user.user_id, user.fullname) for user in result.scalars().all()]


async def count_users():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count(User.id))
        )
        return result.scalar()


async def count_active_users():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count(User.id)).where(User.is_blocked == False)
        )
        return result.scalar()


async def get_daily_users_count(date):
    start_date = datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count(User.id)).where(User.created_at >= start_date, User.created_at < end_date)
        )
        return result.scalar()


async def get_premium_users_count():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count(User.id)).where(User.is_premium == True)
        )
        return result.scalar()
async def increment_user_referral_count(user_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.referral_count += 1
            updated_count = user.referral_count
            await session.commit()
            return updated_count
        return None