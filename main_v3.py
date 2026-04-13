# Запуск: uvicorn step3_pro:app --reload
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Smart Calculator - Stage 3 (Pro)")

FAKE_DB = {"user_123": "gold", "user_456": "silver"}


class OrderRequest(BaseModel):
    item_name: str
    base_price: float


class TaxService:
    def __init__(self, rate: float):
        self.rate = rate

    def apply_tax(self, amount: float) -> float:
        return amount * (1 + self.rate)


def get_tax_service() -> TaxService:
    return TaxService(rate=0.20)

def get_user_status(x_user_id: str = Header(...)) -> str:
    status = FAKE_DB.get(x_user_id)
    if not status:
        raise HTTPException(status_code=401, detail="User not found")
    return status



@app.post("/calculate")
async def calculate_delivery(
        order: OrderRequest,
        status: str = Depends(get_user_status),
        tax_service: TaxService = Depends(get_tax_service)
):
    discount = 0.20 if status == "gold" else 0.10
    base_discounted = order.base_price * (1 - discount)

    final_total = tax_service.apply_tax(base_discounted)

    return {"final_price": round(final_total, 2), "status": status}



@app.post("/enable-tax-free-weekend")
async def enable_tax_free():

    app.dependency_overrides[get_tax_service] = lambda: TaxService(rate=0.0)

    return {"message": "Tax free weekend enabled! All taxes are now 0%."}


@app.post("/disable-tax-free-weekend")
async def disable_tax_free():
    app.dependency_overrides.clear()
    return {"message": "Taxes are back to normal."}