"""Northwind Payments Gateway API service entrypoint."""

import time
from typing import Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.security import verify_cardholder_authentication, route_acquirer_connection

app = FastAPI(
    title="Northwind Payments Gateway",
    version="1.4.0",
    description="Acquirer routing and transaction validation service."
)

class PaymentRequest(BaseModel):
    transaction_id: str = Field(..., example="txn_94829184")
    cart_amount: float = Field(..., gt=0, example=42.50)
    currency: str = Field(default="USD", max_length=3)
    card_token: str = Field(..., example="tok_visa_4242")
    customer_id: str = Field(..., example="cus_91283")

class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    auth_code: str
    routing_latency_ms: float
    timestamp: float

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "svc_payments_gateway"}

@app.post("/api/v1/charge", response_model=PaymentResponse)
async def process_charge(req: PaymentRequest) -> PaymentResponse:
    t0 = time.perf_counter()

    # Step 1: 3-D Secure Cardholder Authentication verification
    authenticated = verify_cardholder_authentication(req.cart_amount)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="3DS verification failed or challenge required."
        )

    # Step 2: Route through secure acquirer connection
    acquirer_status = await route_acquirer_connection(req.card_token, req.cart_amount)
    if not acquirer_status.get("success"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Acquirer link rejected: {acquirer_status.get('reason')}"
        )

    latency = (time.perf_counter() - t0) * 1000
    return PaymentResponse(
        transaction_id=req.transaction_id,
        status="approved",
        auth_code=f"AUTH_{int(time.time())}",
        routing_latency_ms=round(latency, 2),
        timestamp=time.time()
    )
