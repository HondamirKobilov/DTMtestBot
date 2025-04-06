from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, Group


async def create_group(chat_id: int, username: str, title: str):
    async with AsyncSession(engine) as session:
        try:
            new_group = Group(
                chat_id=chat_id,
                username=username,
                title=title
            )
            session.add(new_group)
            await session.commit()
            await session.refresh(new_group)
            return new_group
        except Exception as e:
            print(f"❌ Guruh qo‘shishda xatolik: {e}")
            return None


async def get_group_by_chat_id(chat_id: int):
    """🔍 Chat ID orqali guruhni olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Group).where(Group.chat_id == chat_id))
        return result.scalar_one_or_none()


async def get_all_groups():
    """📋 Barcha guruhlarni olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Group))
        return result.scalars().all()


async def update_group(chat_id: int, **kwargs):
    """✏️ Guruh maʼlumotlarini yangilash"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Group).where(Group.chat_id == chat_id))
        group = result.scalar_one_or_none()

        if group:
            for key, value in kwargs.items():
                if hasattr(group, key):
                    setattr(group, key, value)
            await session.commit()
            return group
        return None


async def delete_group(chat_id: int):
    """🗑 Guruhni o‘chirish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Group).where(Group.chat_id == chat_id))
        group = result.scalar_one_or_none()

        if group:
            await session.delete(group)
            await session.commit()
            return True
        return False
