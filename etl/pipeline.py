# etl/pipeline.py

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from dotenv import load_dotenv
load_dotenv()

from etl.zillow.fetch import fetch_zillow_listings
from etl.zillow.transform import zillow_com1_to_deal
from etl.load import upsert_deal


def get_engine(db_path: str = "workhaus.db") -> Engine:
    return create_engine(f"sqlite:///{db_path}", future=True)


def run_zillow_pipeline(
    db_path: str = "workhaus.db",
    location_query: str | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
    beds_min: int | None = None,
) -> None:
    """
    High-level ETL:
      1) Fetch Zillow listings for given (or default) location/filters
      2) Convert each to Deal
      3) Upsert into SQLite deals table
    """
    engine = get_engine(db_path)

    props = fetch_zillow_listings(
        location_query=location_query,
        price_min=price_min,
        price_max=price_max,
        beds_min=beds_min,
    )

    with engine.begin() as conn:
        for p in props:
            deal = zillow_com1_to_deal(p)
            upsert_deal(conn, deal)
