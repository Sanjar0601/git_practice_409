# Запуск: uvicorn step2_clean:app --reload
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Smart Calculator - Stage 2")

FAKE_DB = {"user_123": "gold", "user_456": "silver"}


class OrderRequest(BaseModel):
    item_name: str
    base_price: float


# ВЫНОСИМ ЛОГИКУ: Зависимость для получения статуса
def get_user_status(x_user_id: str = Header(...)):
    status = FAKE_DB.get(x_user_id)
    if not status:
        raise HTTPException(status_code=401, detail="User not found")
    return status


@app.post("/calculate")
async def calculate_delivery(
        order: OrderRequest,
        status: str = Depends(get_user_status)
):
    discount = 0.20 if status == "gold" else (0.10 if status == "silver" else 0.0)
    price_with_discount = order.base_price * (1 - discount)

    tax_rate = 0.20
    final_total = price_with_discount * (1 + tax_rate)

    return {
        "item": order.item_name,
        "final_price": round(final_total, 2),
        "status": status
    }