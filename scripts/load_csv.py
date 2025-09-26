import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Market, Commodity, Price
import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "wfp_food_prices_global_2025.csv")


def clean_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning and filtering."""
    df = df[df['countryiso3'].notnull()]
    # Only cereals and tubers only for now
    df = df[df['category'] == "cereals and tubers"]
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['price', 'usdprice'])
    return df


def load_data():
    Base.metadata.create_all(bind=engine)

    df = pd.read_csv(CSV_PATH, comment='#')
    df = clean_csv(df)

    session: Session = SessionLocal()

    try:
        # --- 1. Insert unique markets ---
        unique_markets = df[
            ['market_id', 'market', 'admin1', 'admin2', 'countryiso3', 'latitude', 'longitude']].drop_duplicates(
            subset=['market_id'])
        market_objs = [
            Market(
                market_id=row['market_id'],
                market_name=row['market'],
                admin1=row['admin1'],
                admin2=row['admin2'],
                country=row['countryiso3'],
                latitude=row['latitude'],
                longitude=row['longitude']
            ) for _, row in unique_markets.iterrows()
        ]
        session.add_all(market_objs)
        session.commit()
        print(f"Inserted {len(market_objs)} markets")

        # --- 2. Insert unique commodities ---
        unique_commodities = df[['commodity_id', 'commodity', 'category', 'unit']].drop_duplicates(
            subset=['commodity_id'])
        commodity_objs = [
            Commodity(
                commodity_id=row['commodity_id'],
                commodity_name=row['commodity'],
                category=row['category'],
                unit=row['unit']
            ) for _, row in unique_commodities.iterrows()
        ]
        session.add_all(commodity_objs)
        session.commit()
        print(f"Inserted {len(commodity_objs)} commodities")

        # --- 3. Insert all prices ---
        price_objs = [
            Price(
                market_id=row['market_id'],
                commodity_id=row['commodity_id'],
                date=row['date'],
                price=row['price'],
                usd_price=row['usdprice'],
                priceflag=row['priceflag'],
                pricetype=row['pricetype']
            ) for _, row in df.iterrows()
        ]
        session.add_all(price_objs)
        session.commit()
        print(f"Inserted {len(price_objs)} prices")

        print("✨CSV data loaded successfully!")

    except Exception as e:
        session.rollback()
        print("Error loading CSV:", e)
    finally:
        session.close()


if __name__ == "__main__":
    load_data()
