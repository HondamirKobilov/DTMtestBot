from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, History


async def create_history(user_id: int, diagnostika_id: int):
    """✅ Foydalanuvchining diagnostika tarixini qo‘shish"""
    async with AsyncSession(engine) as session:
        try:
            new_history = History(
                user_id=user_id,
                diagnostika_id=diagnostika_id
            )
            session.add(new_history)
            await session.commit()
            await session.refresh(new_history)
            return new_history
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {e}")
            return None


async def get_user_history(user_id: int):
    """✅ Foydalanuvchining diagnostika tarixini olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(History).where(History.user_id == user_id)
        )
        return result.scalars().all()


async def get_history_by_id(history_id: int):
    """✅ Diagnostika tarixini ID bo‘yicha olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(History).where(History.id == history_id)
        )
        return result.scalar_one_or_none()


async def delete_history(history_id: int):
    """✅ Foydalanuvchining diagnostika tarixini o‘chirish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(History).where(History.id == history_id)
        )
        history = result.scalar_one_or_none()

        if history:
            await session.delete(history)
            await session.commit()
            return True
        return False


async def count_history_records():
    """✅ Jami diagnostika tarixlari sonini olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(History.id)))
        return result.scalar()
