from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Market(Base):
    __tablename__ = "markets"

    market_id = Column(Integer, primary_key=True, index=True)
    market_name = Column(String, nullable=False)
    admin1 = Column(String)
    admin2 = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    prices = relationship("Price", back_populates="market")


class Commodity(Base):
    __tablename__ = "commodities"

    commodity_id = Column(Integer, primary_key=True, index=True)
    commodity_name = Column(String, nullable=False)
    category = Column(String)
    unit = Column(String)

    prices = relationship("Price", back_populates="commodity")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.market_id"))
    commodity_id = Column(Integer, ForeignKey("commodities.commodity_id"))
    date = Column(Date)
    price = Column(Float)
    usd_price = Column(Float)
    priceflag = Column(String)
    pricetype = Column(String)

    market = relationship("Market", back_populates="prices")
    commodity = relationship("Commodity", back_populates="prices")