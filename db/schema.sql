-- db/schema.sql for Workhaus

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assessor_parcels (
    parcel_id TEXT PRIMARY KEY,
    address_full TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    owner_name TEXT,
    tax_assessed_value NUMERIC,
    tax_annual NUMERIC,
    land_value NUMERIC,
    improvement_value NUMERIC,
    year_built INTEGER,
    building_sqft INTEGER,
    lot_sqft INTEGER,
    last_updated_ts TEXT
);

CREATE TABLE IF NOT EXISTS deals (
    id TEXT PRIMARY KEY,
    external_source TEXT,
    external_id TEXT,
    parcel_id TEXT,

    address_full TEXT NOT NULL,
    city TEXT,
    state TEXT,
    zip TEXT,
    lat REAL,
    lon REAL,

    list_price NUMERIC,
    estimated_entry_price NUMERIC,
    status TEXT,
    days_on_market INTEGER,

    beds REAL,
    baths REAL,
    sqft INTEGER,
    lot_sqft INTEGER,
    year_built INTEGER,
    property_type TEXT,

    tax_annual NUMERIC,
    tax_assessed_value NUMERIC,
    hoa_monthly NUMERIC,
    insurance_est_monthly NUMERIC,

    arv_estimate NUMERIC,
    preferred_strategy TEXT,

    created_ts TEXT,
    updated_ts TEXT,

    deal_json TEXT
);
