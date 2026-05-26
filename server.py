from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]
FIXED_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "RUB": 92.5,
    "GBP": 0.79,
    "JPY": 157.3, 
    "CNY": 7.24
}

API_URL = "https://api.exchangerate-api.com/v4/latest/USD"


@app.get("/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if amount < 0:
        raise HTTPException(status_code=400, detail="Сумма не может быть отрицательной")
    if from_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта: {from_currency}")
    if to_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта: {to_currency}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, timeout=5)
            if response.status_code == 200:
                rates = response.json().get("rates", FIXED_RATES)
            else:
                rates = FIXED_RATES
    except:
        rates = FIXED_RATES
    amount_in_usd = amount / rates[from_currency]
    converted = amount_in_usd * rates[to_currency]
    rate = rates[to_currency] / rates[from_currency]
    
    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "converted_amount": round(converted, 2),
        "rate": round(rate, 4),
        "source": "live" if rates != FIXED_RATES else "fixed"
    }


@app.get("/currencies")
async def get_currencies():
    return {"currencies": SUPPORTED_CURRENCIES}