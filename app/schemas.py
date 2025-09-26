from pydantic import BaseModel
from datetime import date


class MarketSchema(BaseModel):
    market_id: int
    market_name: str
    admin1: str
    admin2: str
    country: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class CommoditySchema(BaseModel):
    commodity_id: int
    commodity_name: str
    category: str
    unit: str

    class Config:
        from_attributes = True


class PriceSchema(BaseModel):
    market_id: int
    commodity_id: int
    date: date
    price: float
    usd_price: float
    priceflag: str
    pricetype: str

    class Config:
        from_attributes = True
