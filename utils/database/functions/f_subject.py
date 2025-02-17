from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, Subject, Question, diagnostika_subject_association, Answer


async def create_subject(name: str, is_compulsory_subject: bool = False, is_foreign_language: bool = False):
    """✅ Yangi fan yaratish"""
    async with AsyncSession(engine) as session:
        try:
            new_subject = Subject(
                name=name,
                is_compulsory_subject=is_compulsory_subject,
                is_foreign_language=is_foreign_language
            )
            session.add(new_subject)
            await session.commit()
            await session.refresh(new_subject)
            return new_subject
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {e}")
            return None


async def update_subject(subject_id: int, **kwargs):
    """✅ Mavjud fanni yangilash"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Subject).where(Subject.id == subject_id))
        subject = result.scalar_one_or_none()

        if subject:
            for key, value in kwargs.items():
                if hasattr(subject, key):
                    setattr(subject, key, value)

            await session.commit()
            return subject
        return None
async def get_subject_by_id(subject_id: int):
    """✅ Fan ID bo‘yicha ma’lumot olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Subject).where(Subject.id == subject_id))
        return result.scalar_one_or_none()


async def get_all_subjects():
    """✅ Barcha fanlarni olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Subject))
        return result.scalars().all()


async def count_subjects():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(Subject.id)))
        return result.scalar()

async def delete_subject(subject_id: int):
    async with AsyncSession(engine) as session:
        try:
            await session.execute(
                delete(Answer).where(
                    Answer.question_id.in_(
                        select(Question.id).where(Question.subject_id == subject_id)
                    )
                )
            )
            await session.execute(delete(Question).where(Question.subject_id == subject_id))
            await session.execute(delete(diagnostika_subject_association).where(diagnostika_subject_association.c.subject_id == subject_id))
            await session.execute(delete(Subject).where(Subject.id == subject_id))
            await session.commit()
            return True
        except Exception as e:
            print(f"❌ Fanni o‘chirishda xatolik: {e}")
            return False