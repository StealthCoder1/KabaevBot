from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, UniqueConstraint
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(32), nullable=False, default="user")
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    date_start = Column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(64), nullable=False, index=True)
    user_telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True, index=True)
    price_range = Column(String(255), nullable=True)
    message_text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AutoInTransitPost(Base):
    __tablename__ = "auto_in_transit_posts"
    __table_args__ = (
        UniqueConstraint("channel_id", "message_id", name="uq_auto_in_transit_posts_channel_message"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(BigInteger, nullable=False, index=True)
    media_group_id = Column(String(255), nullable=True, index=True)
    posted_at = Column(DateTime, nullable=True, index=True)
