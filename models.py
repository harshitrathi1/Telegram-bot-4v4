from datetime import datetime, date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime, Date, Text, ForeignKey

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True) # Telegram ID
    username: Mapped[str]=mapped_column(String(100), default="")
    balance: Mapped[int]=mapped_column(Integer, default=0)
    referred_by: Mapped[int|None]=mapped_column(Integer, nullable=True)
    is_banned: Mapped[bool]=mapped_column(Boolean, default=False)
    is_admin: Mapped[bool]=mapped_column(Boolean, default=False)
    last_daily: Mapped[date|None]=mapped_column(Date, nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__="tasks"
    id: Mapped[int]=mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]=mapped_column(String(180))
    description: Mapped[str]=mapped_column(Text, default="")
    reward: Mapped[int]=mapped_column(Integer, default=1)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_by: Mapped[int]=mapped_column(Integer)

class TaskClaim(Base):
    __tablename__="task_claims"
    id: Mapped[int]=mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int]=mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int]=mapped_column(Integer)
    claimed_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__="transactions"
    id: Mapped[int]=mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int]=mapped_column(Integer)
    amount: Mapped[int]=mapped_column(Integer)
    reason: Mapped[str]=mapped_column(String(250))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class AdminSession(Base):
    __tablename__="admin_sessions"
    user_id: Mapped[int]=mapped_column(Integer, primary_key=True)
    expires_at: Mapped[datetime]=mapped_column(DateTime)
