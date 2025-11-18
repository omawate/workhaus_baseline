# main.py

from etl.pipeline import run_zillow_pipeline

if __name__ == "__main__":
    # Uses defaults from env (cape cod, price range, etc.)
    run_zillow_pipeline(db_path="workhaus.db")
    print("Zillow → Deal → SQLite ETL complete.")
