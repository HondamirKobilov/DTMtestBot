from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, Question


async def create_question(question_text: str, subject_id: int, diagnostika_id: int, image: str = None,
                          is_mandatory: bool = False):
    """✅ Yangi savol qo‘shish (majburiy yoki oddiy)"""
    async with AsyncSession(engine) as session:
        try:
            new_question = Question(
                question_text=question_text,
                subject_id=subject_id,
                diagnostika_id=diagnostika_id,
                image=image,
                is_mandatory=is_mandatory  # ✅ Majburiy yoki oddiy savolni ajratish
            )
            session.add(new_question)
            await session.commit()
            await session.refresh(new_question)
            return new_question
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {e}")
            return None


async def get_tests_by_diagnostika_and_subject(diagnostika_id: int, subject_id: int, is_mandatory: bool = None):
    """✅ Diagnostika va fanga tegishli testlarni olish, majburiy yoki oddiy ajratish"""
    async with AsyncSession(engine) as session:
        query = select(Question).where(
            Question.diagnostika_id == diagnostika_id,
            Question.subject_id == subject_id
        )
        if is_mandatory is not None:
            query = query.where(Question.is_mandatory == is_mandatory)

        result = await session.execute(query)
        return result.scalars().all()


async def count_tests_by_diagnostika_and_subject(diagnostika_id: int, subject_id: int,
                                                 is_mandatory: bool = None) -> int:
    """✅ Diagnostika va fanga tegishli testlar sonini hisoblash, majburiy yoki oddiy ajratish"""
    async with AsyncSession(engine) as session:
        query = select(func.count(Question.id)).where(
            Question.diagnostika_id == diagnostika_id,
            Question.subject_id == subject_id
        )
        if is_mandatory is not None:
            query = query.where(Question.is_mandatory == is_mandatory)

        result = await session.execute(query)
        return result.scalar() or 0


async def delete_tests_by_diagnostika_and_subject(diagnostika_id: int, subject_id: int, is_mandatory: bool = None):
    """🗑 Diagnostika va fanga tegishli testlarni bazadan o‘chirish, majburiy yoki oddiy ajratish"""
    async with AsyncSession(engine) as session:
        query = select(Question).where(
            Question.diagnostika_id == diagnostika_id,
            Question.subject_id == subject_id
        )
        if is_mandatory is not None:
            query = query.where(Question.is_mandatory == is_mandatory)

        result = await session.execute(query)
        tests = result.scalars().all()

        if not tests:
            return False  # ❌ Testlar mavjud emas

        for test in tests:
            await session.delete(test)
        await session.commit()
        return True  # ✅ Testlar o‘chirildi


async def get_mandatory_tests(subject_id: int, diagnostika_id: int):
    """✅ Berilgan fanga oid majburiy testlarni olish"""
    return await get_tests_by_diagnostika_and_subject(diagnostika_id, subject_id, is_mandatory=True)


async def get_regular_tests(subject_id: int, diagnostika_id: int):
    """✅ Berilgan fanga oid oddiy testlarni olish"""
    return await get_tests_by_diagnostika_and_subject(diagnostika_id, subject_id, is_mandatory=False)
