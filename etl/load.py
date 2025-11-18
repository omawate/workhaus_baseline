# etl/load.py
import json
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection
from deal.deal_object import Deal


def deal_to_row(deal: Deal) -> dict[str, Any]:
    """
    Flatten a Deal object into scalar columns for the `deals` table,
    plus a JSON string for `deal_json`.
    """
    # IMPORTANT: mode="json" so datetimes become ISO strings
    d = deal.model_dump(mode="json")

    now_iso = datetime.utcnow().isoformat()

    return {
        "id": deal.meta.deal_id,
        "external_source": deal.meta.source,
        "external_id": deal.meta.source_id,

        "parcel_id": deal.identification.parcel_id,

        "address_full": deal.identification.address_full,
        "city": deal.identification.city,
        "state": deal.identification.state,
        "zip": deal.identification.zip,
        "lat": deal.identification.lat,
        "lon": deal.identification.lon,

        "list_price": deal.acquisition.list_price,
        "estimated_entry_price": deal.acquisition.estimated_entry_price,
        "status": deal.acquisition.status,
        "days_on_market": deal.acquisition.days_on_market,

        "beds": deal.physical.beds,
        "baths": deal.physical.baths,
        "sqft": deal.physical.sqft,
        "lot_sqft": deal.physical.lot_sqft,
        "year_built": deal.physical.year_built,
        "property_type": deal.physical.property_type,

        "tax_annual": deal.financial.tax_annual,
        "tax_assessed_value": deal.financial.tax_assessed_value,
        "hoa_monthly": deal.financial.hoa_monthly,
        "insurance_est_monthly": deal.financial.insurance_est_monthly,

        "arv_estimate": deal.valuation.arv_estimate,

        "preferred_strategy": deal.strategy.preferred_strategy,

        # meta timestamps as ISO strings
        "created_ts": deal.meta.created_ts.isoformat(),
        "updated_ts": now_iso,

        # Full Deal as JSON string
        "deal_json": json.dumps(d),
    }


def upsert_deal(conn: Connection, deal: Deal) -> None:
    """
    Upsert a Deal into the `deals` table using SQLite ON CONFLICT.
    """
    row = deal_to_row(deal)

    stmt = text("""
        INSERT INTO deals (
            id, external_source, external_id,
            parcel_id,
            address_full, city, state, zip, lat, lon,
            list_price, estimated_entry_price, status, days_on_market,
            beds, baths, sqft, lot_sqft, year_built, property_type,
            tax_annual, tax_assessed_value, hoa_monthly, insurance_est_monthly,
            arv_estimate, preferred_strategy,
            created_ts, updated_ts,
            deal_json
        ) VALUES (
            :id, :external_source, :external_id,
            :parcel_id,
            :address_full, :city, :state, :zip, :lat, :lon,
            :list_price, :estimated_entry_price, :status, :days_on_market,
            :beds, :baths, :sqft, :lot_sqft, :year_built, :property_type,
            :tax_annual, :tax_assessed_value, :hoa_monthly, :insurance_est_monthly,
            :arv_estimate, :preferred_strategy,
            :created_ts, :updated_ts,
            :deal_json
        )
        ON CONFLICT(id) DO UPDATE SET
            external_source = excluded.external_source,
            external_id = excluded.external_id,
            parcel_id = excluded.parcel_id,
            address_full = excluded.address_full,
            city = excluded.city,
            state = excluded.state,
            zip = excluded.zip,
            lat = excluded.lat,
            lon = excluded.lon,
            list_price = excluded.list_price,
            estimated_entry_price = excluded.estimated_entry_price,
            status = excluded.status,
            days_on_market = excluded.days_on_market,
            beds = excluded.beds,
            baths = excluded.baths,
            sqft = excluded.sqft,
            lot_sqft = excluded.lot_sqft,
            year_built = excluded.year_built,
            property_type = excluded.property_type,
            tax_annual = excluded.tax_annual,
            tax_assessed_value = excluded.tax_assessed_value,
            hoa_monthly = excluded.hoa_monthly,
            insurance_est_monthly = excluded.insurance_est_monthly,
            arv_estimate = excluded.arv_estimate,
            preferred_strategy = excluded.preferred_strategy,
            updated_ts = excluded.updated_ts,
            deal_json = excluded.deal_json;
    """)

    conn.execute(stmt, row)
