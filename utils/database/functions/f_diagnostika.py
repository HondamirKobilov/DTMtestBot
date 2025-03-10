import asyncio
from datetime import datetime

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, Diagnostika, diagnostika_subject_association, Question, Subject, Answer, \
    History, user_diagnostika_association
from sqlalchemy.orm import selectinload


async def create_diagnostika(name: str, finished_at: datetime):
    """✅ Yangi diagnostika qo‘shish"""
    async with AsyncSession(engine) as session:
        try:
            new_diagnostika = Diagnostika(name=name, finished_at=finished_at)  # ✅ Tugash vaqti qo‘shildi
            session.add(new_diagnostika)
            await session.commit()
            await session.refresh(new_diagnostika)
            return new_diagnostika
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {e}")
            return None



async def update_diagnostika(diagnostika_id: int, **kwargs):
    """✅ Diagnostikani yangilash"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Diagnostika).where(Diagnostika.id == diagnostika_id))
        diagnostika = result.scalar_one_or_none()

        if diagnostika:
            for key, value in kwargs.items():
                if hasattr(diagnostika, key):
                    setattr(diagnostika, key, value)

            await session.commit()
            return diagnostika
        return None

async def delete_diagnostika(diagnostika_id: int):
    async with AsyncSession(engine) as session:
        try:
            await session.execute(
                delete(Answer).where(Answer.question_id.in_(
                    select(Question.id).where(Question.diagnostika_id == diagnostika_id)
                ))
            )
            await session.execute(
                delete(Question).where(Question.diagnostika_id == diagnostika_id)
            )
            await session.execute(
                delete(History).where(History.diagnostika_id == diagnostika_id)
            )
            await session.execute(
                delete(diagnostika_subject_association).where(diagnostika_subject_association.c.diagnostika_id == diagnostika_id)
            )
            await session.execute(
                delete(user_diagnostika_association).where(user_diagnostika_association.c.diagnostika_id == diagnostika_id)
            )
            await session.execute(delete(Diagnostika).where(Diagnostika.id == diagnostika_id))
            await session.commit()
            return True
        except Exception as e:
            print(f"❌ Diagnostikani o‘chirishda xatolik: {e}")
            return False

async def get_diagnostika_by_id(diagnostika_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Diagnostika).where(Diagnostika.id == diagnostika_id))
        return result.scalar_one_or_none()


async def get_all_diagnostikas():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Diagnostika))
        return result.scalars().all()


async def count_diagnostikas():
    """✅ Jami diagnostikalar sonini olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(Diagnostika.id)))
        return result.scalar()

async def is_diagnostika_linked_to_subject(diagnostika_id: int, subject_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(diagnostika_subject_association).where(
                diagnostika_subject_association.c.diagnostika_id == diagnostika_id,
                diagnostika_subject_association.c.subject_id == subject_id
            )
        )
        return result.first() is not None

async def get_tests_by_diagnostika_and_subject(diagnostika_id: int, subject_id: int, is_mandatory: bool = None):
    """Diagnostika va fan bo‘yicha mos testlarni olish (majburiy yoki oddiy)"""
    async with AsyncSession(engine) as session:
        query = select(Question).where(
            Question.subject_id == subject_id,
            Question.diagnostika_id == diagnostika_id
        )
        if is_mandatory is not None:  # Agar majburiy yoki oddiy testlar kerak bo‘lsa, shart qo‘shamiz
            query = query.where(Question.is_mandatory == is_mandatory)

        result = await session.execute(query)
        return result.scalars().all()

async def link_subject_to_diagnostika(subject_id: int, diagnostika_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Diagnostika)
            .options(selectinload(Diagnostika.subjects))  # ✅ Lazy loading muammosini hal qiladi
            .filter(Diagnostika.id == diagnostika_id)
        )
        diagnostika = result.scalars().first()

        subject = await session.get(Subject, subject_id)

        if diagnostika and subject:
            if subject not in diagnostika.subjects:
                diagnostika.subjects.append(subject)
                await session.commit()
                return True
            return False
        return None

async def count_questions_for_diagnostika(diagnostika_id: int, subject_id: int) -> int:
    async with AsyncSession(engine) as session:
        stmt = (
            select(func.count(Question.id))
            .where(
                Question.subject_id == subject_id,
                Question.diagnostika_id == diagnostika_id
            )
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

async def count_diagnostikas_by_subject(subject_id: int) -> int:
    async with AsyncSession(engine) as session:
        stmt = select(diagnostika_subject_association).where(diagnostika_subject_association.c.subject_id == subject_id)
        result = await session.execute(stmt)
        return len(result.all())

async def count_tests_by_diagnostika(diagnostika_id: int) -> int:
    async with AsyncSession(engine) as session:
        stmt = select(diagnostika_subject_association.c.subject_id).where(
            diagnostika_subject_association.c.diagnostika_id == diagnostika_id
        )
        result = await session.execute(stmt)
        subject_ids = [row[0] for row in result.all()]
        if not subject_ids:
            return 0
        stmt = select(Question).where(Question.subject_id.in_(subject_ids))
        result = await session.execute(stmt)
        return len(result.all())

async def delete_diagnostika_subject_link(diagnostika_id: int, subject_id: int):
    async with AsyncSession(engine) as session:
        stmt = delete(diagnostika_subject_association).where(
            diagnostika_subject_association.c.diagnostika_id == diagnostika_id,
            diagnostika_subject_association.c.subject_id == subject_id
        )
        await session.execute(stmt)
        await session.commit()
async def check_diagnostika_status():
    while True:
        async with AsyncSession(engine) as session:
            now = datetime.now()
            stmt = select(Diagnostika).where(Diagnostika.finished_at <= now, Diagnostika.status == True)
            result = await session.execute(stmt)
            diagnostikas = result.scalars().all()
            for diagnostika in diagnostikas:
                diagnostika.status = False
                session.add(diagnostika)
            if diagnostikas:
                await session.commit()
                print(f"🔄 {len(diagnostikas)} ta diagnostika avtomatik o‘chirildi.")
        await asyncio.sleep(60)


async def get_diagnostika_detail_buttons(diagnostika_id: int):
    from keyboards.inline.inline_admin import generate_diagnostika_buttons  # ✅ Importni shu yerda qilish

    diagnostika = await get_diagnostika_by_id(diagnostika_id)

    if diagnostika:
        status_emoji = "🟡" if diagnostika.status else "🔴"
        keyboard = await generate_diagnostika_buttons(diagnostika.id)
        return f"📌 Tanlangan diagnostika: {diagnostika.name}\n\n{status_emoji} Status", keyboard
    else:
        return "❌ Diagnostika topilmadi!", None

