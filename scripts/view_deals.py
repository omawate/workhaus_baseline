from sqlalchemy import create_engine
import pandas as pd

DB_PATH = "workhaus.db"

def main():
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

    query = """
        SELECT
            address_full,
            city,
            state,
            zip,
            list_price,
            beds,
            baths,
            sqft,
            (CASE
                WHEN sqft IS NOT NULL AND sqft > 0
                THEN list_price * 1.0 / sqft
                ELSE NULL
            END) AS price_per_sqft
        FROM deals
        ORDER BY list_price
        LIMIT 25;
    """

    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()