from asyncpg import DuplicateDatabaseError, connect
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, VARCHAR, Integer, Table, UniqueConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from data.config import *
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, pool_size=200, max_overflow=2000)
Base = declarative_base()

async def create_database(db_name=DB_NAME):
    conn_info = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/postgres'
    conn = await connect(conn_info)
    try:
        await conn.execute(f'CREATE DATABASE {db_name}')
        print(f'Database {db_name} created successfully.')
    except DuplicateDatabaseError:
        print(f'Database {db_name} already exists.')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        await conn.close()


user_diagnostika_association = Table(
    "user_diagnostika_association", Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column("diagnostika_id", BigInteger, ForeignKey("diagnostika.id"), primary_key=True)
)

diagnostika_subject_association = Table(
    "diagnostika_subject_association", Base.metadata,
    Column("diagnostika_id", BigInteger, ForeignKey("diagnostika.id"), primary_key=True),
    Column("subject_id", BigInteger, ForeignKey("subjects.id"), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    language = Column(String(2), nullable=False, default="uz")
    fullname = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    region = Column(Integer, nullable=True)
    district = Column(Integer, nullable=True)
    username = Column(String, unique=True, nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False)
    is_premium = Column(Boolean, nullable=False, default=False)
    referral_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=toshkent_now)
    updated_at = Column(DateTime, default=toshkent_now, onupdate=toshkent_now)
    diagnostikas = relationship("Diagnostika", secondary=user_diagnostika_association, back_populates="users")
    history = relationship("History", back_populates="user")

class ReferralCount(Base):
    __tablename__ = 'ref_count'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    count = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<ReferralCount id={self.id} count={self.count}>"

class Diagnostika(Base):
    __tablename__ = 'diagnostika'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    users = relationship("User", secondary=user_diagnostika_association, back_populates="diagnostikas")
    created_at = Column(DateTime, default=toshkent_now)
    updated_at = Column(DateTime, default=toshkent_now, onupdate=toshkent_now)
    finished_at = Column(DateTime, nullable=True)  # ✅ Tugash vaqti
    status = Column(Boolean, default=True)  # ✅ Diagnostika holati (True - aktiv, False - tugagan)
    subjects = relationship(
        "Subject",
        secondary=diagnostika_subject_association,
        back_populates="diagnostikas"
    )
    questions = relationship("Question", back_populates="diagnostika", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    is_compulsory_subject = Column(Boolean, nullable=False, default=False)
    is_foreign_language = Column(Boolean, nullable=False, default=False)
    diagnostikas = relationship("Diagnostika", secondary=diagnostika_subject_association,
                                back_populates="subjects")
    questions = relationship("Question", back_populates="subject")


class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question_text = Column(String, nullable=False)
    image = Column(String, nullable=True)
    subject_id = Column(BigInteger, ForeignKey("subjects.id"), nullable=False)
    diagnostika_id = Column(BigInteger, ForeignKey("diagnostika.id"), nullable=False)
    is_mandatory = Column(Boolean, nullable=False, default=False)

    subject = relationship("Subject", back_populates="questions")
    diagnostika = relationship("Diagnostika", back_populates="questions")  # ✅ Diagnostika bilan bog‘lash

    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    question_id = Column(BigInteger, ForeignKey("questions.id"), nullable=False)
    question = relationship("Question", back_populates="answers")


class History(Base):
    __tablename__ = "history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    diagnostika_id = Column(BigInteger, ForeignKey("diagnostika.id"), nullable=False)
    created_at = Column(DateTime, default=toshkent_now)
    user = relationship("User", back_populates="history")

class Result(Base):
    __tablename__ = "results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    diagnostika_id = Column(BigInteger, ForeignKey("diagnostika.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    subject1_name = Column(String, nullable=False)  # 1-fan nomi
    subject2_name = Column(String, nullable=False)  # 2-fan nomi
    correct_answers_subject1 = Column(Integer, nullable=False, default=0)  # 1-fan to‘g‘ri javoblar soni
    correct_answers_subject2 = Column(Integer, nullable=False, default=0)  # 2-fan to‘g‘ri javoblar soni
    correct_answers_mandatory = Column(Integer, nullable=False, default=0)  # Majburiy fan to‘g‘ri javoblar soni
    total_score = Column(Integer, nullable=False, default=0)  # Jami ball
    completed_at = Column(DateTime, default=toshkent_now)  # Yakunlangan vaqti
    all_answer_ids = Column(JSONB, nullable=False, default=list)
    correct_answer_ids = Column(JSONB, nullable=False, default=list)  # ✅ To‘g‘ri javoblar ID lari
    wrong_answer_ids = Column(JSONB, nullable=False, default=list)  # ✅ Noto‘g‘ri javoblar ID lari
    duration_time = Column(String, nullable=False, default="00:00:00") # ⏳ Testni qancha vaqt bajargan

    user = relationship("User", back_populates="results")
    diagnostika = relationship("Diagnostika", back_populates="results")

    User.results = relationship("Result", back_populates="user", cascade="all, delete-orphan")
    Diagnostika.results = relationship("Result", back_populates="diagnostika", cascade="all, delete-orphan")

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String, nullable=False)
    title = Column(String, nullable=False)

    def __repr__(self):
        return f"<Group(id={self.id}, chat_id={self.chat_id}, username='@{self.username}', title='{self.title}')>"

class ReferralHistory(Base):
    __tablename__ = "referral_history"

    id = Column(Integer, primary_key=True, autoincrement=True)         # Optional: aniqlik uchun
    inviter_id = Column(BigInteger, nullable=False)                   # Taklif qilgan user
    invited_id = Column(BigInteger, nullable=False)                   # Taklif qilingan user
    diagnostika_id = Column(BigInteger, nullable=False)               # Qaysi diagnostika uchun taklif qilingan

    __table_args__ = (
        UniqueConstraint("inviter_id", "invited_id", "diagnostika_id", name="unique_referral_diagnostika"),
    )

    def __repr__(self):
        return f"<ReferralHistory inviter={self.inviter_id}, invited={self.invited_id}, diagnostika={self.diagnostika_id}>"
