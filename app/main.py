from fastapi import FastAPI, Depends, Query, HTTPException
from typing import List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import engine, Base, get_db
from app.models import Market, Commodity, Price
from app.schemas import MarketSchema, CommoditySchema, PriceSchema

Base.metadata.create_all(bind=engine)

app = FastAPI(title="WFP Food Prices API")


@app.get("/health")
def health():
    return {"message": "WFP Food Prices API is running!"}


@app.get("/")
def home():
    return {"message": "This is the WFP Food Prices API homepage!"}


@app.get("/markets", response_model=List[MarketSchema])
def get_markets(db: Session = Depends(get_db)):
    return db.query(Market).all()


@app.get("/markets/{market_id}", response_model=MarketSchema)
def get_market(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.market_id == market_id).first()  # type: ignore
    if not market:
        raise HTTPException(status_code=404, detail={
            "error_code": 404,
            "message": "Market not found"
        })
    return market


@app.get("/commodities", response_model=List[CommoditySchema])
def get_commodities(db: Session = Depends(get_db)):
    return db.query(Commodity).all()


@app.get("/commodities/{commodity_id}", response_model=CommoditySchema)
def get_commodity(commodity_id: int, db: Session = Depends(get_db)):
    commodity = db.query(Commodity).filter(Commodity.commodity_id == commodity_id).first()  # type: ignore
    if not commodity:
        raise HTTPException(status_code=404, detail={
            "error_code": 404,
            "message": "Commodity not found"
        })
    return commodity


@app.get("/prices", response_model=List[PriceSchema])
def get_prices(
        market_id: int | None = None,
        commodity_id: int | None = None,
        start_date: date | None = Query(None, description="Start of date range (YYYY-MM-DD)"),
        end_date: date | None = Query(None, description="End of date range (YYYY-MM-DD)"),
        db: Session = Depends(get_db)
):
    """
        Returns prices with optional filters:
        - market_id
        - commodity_id
        - start_date / end_date (inclusive)
    """

    query = db.query(Price)

    if market_id is not None:
        query = query.filter(Price.market_id == market_id)  # type: ignore
    if commodity_id is not None:
        query = query.filter(Price.commodity_id == commodity_id)  # type: ignore

    if start_date is not None:
        query = query.filter(Price.date >= start_date)

    if end_date is not None:
        query = query.filter(Price.date <= end_date)

    return query.all()


@app.get("/latest-prices", response_model=List[PriceSchema])
def get_latest_prices(
        market_id: int | None = None,
        commodity_id: int | None = None,
        db: Session = Depends(get_db)
):
    """Returns the latest price for each commodity in each market.
    Optional filters: market_id, commodity_id
    """
    subquery = (
        db.query(
            Price.market_id,
            Price.commodity_id,
            func.max(Price.date).label("latest_date")
        )
        .group_by(Price.market_id, Price.commodity_id)
        .subquery()
    )

    query = (
        db.query(Price)
        .join(
            subquery,
            and_(
                Price.market_id == subquery.c.market_id,
                Price.commodity_id == subquery.c.commodity_id,
                Price.date == subquery.c.latest_date,
            )
        )
    )

    if market_id is not None:
        query = query.filter(Price.market_id == market_id)  # type: ignore
    if commodity_id is not None:
        query = query.filter(Price.commodity_id == commodity_id)  # type: ignore

    return query.all()
