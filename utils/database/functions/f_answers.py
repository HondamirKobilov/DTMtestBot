from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models import engine, Answer


async def create_answer(text: str, is_correct: bool, question_id: int):
    """✅ Yangi javob variantini qo‘shish"""
    async with AsyncSession(engine) as session:
        try:
            new_answer = Answer(
                text=text,
                is_correct=is_correct,
                question_id=question_id
            )
            session.add(new_answer)
            await session.commit()
            await session.refresh(new_answer)
            return new_answer
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {e}")
            return None


async def update_answer(answer_id: int, **kwargs):
    """✅ Javob variantini yangilash"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Answer).where(Answer.id == answer_id))
        answer = result.scalar_one_or_none()

        if answer:
            for key, value in kwargs.items():
                if hasattr(answer, key):
                    setattr(answer, key, value)

            await session.commit()
            return answer
        return None


async def delete_answer(answer_id: int):
    """✅ Javob variantini o‘chirish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Answer).where(Answer.id == answer_id))
        answer = result.scalar_one_or_none()

        if answer:
            await session.delete(answer)
            await session.commit()
            return True
        return False


async def get_answer_by_id(answer_id: int):
    """✅ Javob ID bo‘yicha ma’lumot olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Answer).where(Answer.id == answer_id))
        return result.scalar_one_or_none()


async def get_answers_by_question(question_id: int):
    """✅ Berilgan savolga tegishli barcha javoblarni olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Answer).where(Answer.question_id == question_id))
        return result.scalars().all()


async def get_correct_answer(question_id: int):
    """✅ Savolning to‘g‘ri javobini olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Answer).where(Answer.question_id == question_id, Answer.is_correct == True)
        )
        return result.scalar_one_or_none()


async def count_answers():
    """✅ Jami javoblar sonini olish"""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(Answer.id)))
        return result.scalar()
