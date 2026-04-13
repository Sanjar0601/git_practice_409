from datetime import time

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Smart Calculator - Stage 1")

FAKE_DB = {
    "user_123": "gold",
    "user_456": "silver",
    "user_789": "basic"
}


class OrderRequest(BaseModel):
    item_name: str
    base_price: float


class RateLimiter:
    def __init__(self, limit: int):
        self.limit = limit
        self.user_history = {}

    def __call__(self, user_id:str = Header(...)):
        current_time = time.time()
        user_times = self.user_history.setdefault(user_id, [])
        user_times = [t for t in user_times if current_time - t < 60]

        if len(user_times) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        user_times.append(current_time)
        self.user_history[user_id] = user_times
        return user_times
    
print("salom from Manuchera")
@app.post("/calculate")
async def calculate_delivery(order: OrderRequest, x_user_id: str = Header(default=None)):
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header is missing")

    user_status = FAKE_DB.get(x_user_id)
    if not user_status:
        raise HTTPException(status_code=401, detail="Unknown user")

    if user_status == "gold":
        discount = 0.20
    elif user_status == "silver":
        discount = 0.10
    else:
        discount = 0.0
    price_with_discount = order.base_price * (1 - discount)

    tax_rate = 0.20
    final_total = price_with_discount * (1 + tax_rate)

    return {
        "item": order.item_name,
        "original_price": order.base_price,
        "final_price": round(final_total, 2),
        "applied_discount": discount,
        "status": user_status
    }