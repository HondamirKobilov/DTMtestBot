from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, Diagnostika, diagnostika_subject_association, Question, Subject, Answer, \
    History, user_diagnostika_association
from sqlalchemy.orm import selectinload


async def create_diagnostika(name: str):
    """✅ Yangi diagnostika qo‘shish"""
    async with AsyncSession(engine) as session:
        try:
            new_diagnostika = Diagnostika(name=name)
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
    """✅ Berilgan diagnostika va fanga tegishli testlar sonini hisoblash"""
    async with AsyncSession(engine) as session:
        stmt = (
            select(func.count(Question.id))
            .where(
                Question.subject_id == subject_id,  # ✅ Aynan shu fanga tegishli testlar
                Question.diagnostika_id == diagnostika_id  # ✅ Aynan shu diagnostikaga tegishli testlar
            )
        )
        result = await session.execute(stmt)
        return result.scalar() or 0  # ✅ Agar natija None bo‘lsa, 0 qaytariladi


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
