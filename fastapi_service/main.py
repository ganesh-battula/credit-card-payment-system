import os
import uuid
import random
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from fastapi_service.database import get_db
from fastapi_service.models import DBCard, DBTransaction

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "django-insecure-credit-card-payment-system-secret-key-prod-test-998877"
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

app = FastAPI(
    title="Payment Processing Engine (FastAPI)",
    description="Asynchronous payment simulation engine sharing MySQL with Django.",
    version="1.0.0"
)


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Expired or invalid JWT token")


class PaymentRequest(BaseModel):
    card_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="INR", max_length=3)


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str
    message: str
    failure_reason: Optional[str] = None


@app.post("/payments/process", response_model=PaymentResponse, tags=["Payments"])
async def process_payment(
    payload: PaymentRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # 1. Validate Card Ownership
    card = db.query(DBCard).filter(
        DBCard.id == payload.card_id, 
        DBCard.user_id == current_user_id
    ).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found or ownership mismatch")

    # 2. Stage Transaction in PENDING state
    tx_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
    tx = DBTransaction(
        transaction_id=tx_id,
        user_id=current_user_id,
        card_id=card.id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    # 3. Simulate Gateway Delay
    await asyncio.sleep(1.0)

    # 4. Gateway Decision Simulation (80% Success, 20% Decline)
    success = random.choices([True, False], weights=[80, 20])[0]

    if success:
        tx.status = "SUCCESS"
        tx.failure_reason = None
        message = "Payment completed successfully"
    else:
        tx.status = "FAILED"
        tx.failure_reason = random.choice([
            "Insufficient card balance",
            "Expired card",
            "Bank declined transaction",
            "Security verification timeout"
        ])
        message = f"Transaction declined: {tx.failure_reason}"

    db.commit()

    return {
        "transaction_id": tx.transaction_id,
        "status": tx.status,
        "amount": float(tx.amount),
        "currency": tx.currency,
        "message": message,
        "failure_reason": tx.failure_reason
    }