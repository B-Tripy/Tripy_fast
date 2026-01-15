# database/recommend_mysql.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select, update, and_
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# -----------------------------
# DB 엔진 및 세션
# -----------------------------
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# -----------------------------
# DB 모델
# -----------------------------
from sqlalchemy import Column, Integer, String, Text

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    nickname = Column(String(50))
    email = Column(String(120), unique=True)
    password = Column(String(200))
    createdAt = Column(String, default=datetime.utcnow)

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    score = Column(Integer, default=0)

class UserTrip(Base):
    __tablename__ = "usertrip"
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, index=True)
    tripid = Column(Integer, index=True)

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, index=True)
    location = Column(String(255))
    description = Column(Text)

# -----------------------------
# DB 유틸리티 함수
# -----------------------------

# 1️⃣ 유저 여행 조회
async def get_user_trips(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Trip.id, Trip.title, Trip.description)
            .join(UserTrip, UserTrip.tripid == Trip.id)
            .where(UserTrip.userid == user_id)
        )
        return result.all()

# 2️⃣ Trip 점수 업데이트
async def update_trip_scores(satisfaction: list):
    async with AsyncSessionLocal() as session:
        for s in satisfaction:
            if "trip_id" not in s:
                continue
            await session.execute(
                update(Trip)
                .where(Trip.id == s["trip_id"])
                .values(score=s["score"])
            )
        await session.commit()

# 3️⃣ 즐겨찾기 CRUD

async def get_bookmarks(userid: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Bookmark).where(Bookmark.userid == userid)
        )
        return result.scalars().all()

async def add_bookmark(userid: int, location: str, description: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Bookmark).where(and_(Bookmark.userid == userid, Bookmark.location == location))
        )
        exists = result.scalars().first()
        if exists:
            return False
        bookmark = Bookmark(userid=userid, location=location, description=description)
        session.add(bookmark)
        await session.commit()
        return True

async def remove_bookmark(userid: int, location: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Bookmark).where(and_(Bookmark.userid == userid, Bookmark.location == location))
        )
        bookmark = result.scalars().first()
        if not bookmark:
            return False
        await session.delete(bookmark)
        await session.commit()
        return True
