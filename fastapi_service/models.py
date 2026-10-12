from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from fastapi_service.database import Base


class DBCard(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    masked_card_number = Column(String(20))


class DBTransaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(64), unique=True, index=True)
    user_id = Column(Integer)
    card_id = Column(Integer, nullable=True)
    amount = Column(Numeric(12, 2))
    currency = Column(String(3), default="INR")
    status = Column(String(10), default="PENDING")
    failure_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)