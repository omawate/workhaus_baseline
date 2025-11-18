# etl/zillow/transform.py

from datetime import datetime
from typing import Dict

from deal.deal_object import (
    Deal,
    Identification,
    Acquisition,
    Physical,
    Meta,
    Photo,
)


def zillow_com1_to_deal(z: Dict) -> Deal:
    """
    Map a single zillow-com1 'propertyExtendedSearch' item into a Deal.

    Expected keys commonly seen:
      - 'zpid'
      - 'address' (full string)
      - 'price'
      - 'beds'
      - 'baths'
      - 'area'
      - 'latLong' -> { 'latitude', 'longitude' }
      - 'imgSrc'
      - 'listingType' (e.g. FOR_SALE)
    """

    # Full address might look like: "15 Seashell Ln, Dennis, MA 02638"
    full_addr = z.get("address", "") or ""
    parts = [part.strip() for part in full_addr.split(",")]

    street = parts[0] if len(parts) > 0 else ""
    city = parts[1] if len(parts) > 1 else ""
    state = ""
    zipcode = ""

    if len(parts) > 2:
        state_zip_parts = parts[2].split()
        if len(state_zip_parts) >= 1:
            state = state_zip_parts[0]
        if len(state_zip_parts) >= 2:
            zipcode = state_zip_parts[-1]

    latlong = z.get("latLong") or {}
    lat = latlong.get("latitude")
    lon = latlong.get("longitude")

    identification = Identification(
        address_full=full_addr,
        street=street,
        city=city,
        state=state,
        zip=zipcode,
        lat=lat,
        lon=lon,
        parcel_id=None,  # to be filled by assessor later
    )

    acquisition = Acquisition(
        list_price=z.get("price"),
        estimated_entry_price=z.get("price"),
        source="zillow_com1",
        status=z.get("listingType"),   # e.g. "FOR_SALE"
        days_on_market=None,
        last_update_ts=None,
    )

    photo_obj = None
    img_src = z.get("imgSrc")
    if img_src:
        photo_obj = Photo(url=img_src, label="primary")

    beds = z.get("beds") or z.get("bedrooms")
    baths = z.get("baths") or z.get("bathrooms")
    sqft = z.get("area") or z.get("livingArea")

    physical = Physical(
        beds=beds,
        baths=baths,
        sqft=sqft,
        lot_sqft=None,
        year_built=z.get("yearBuilt"),
        property_type="SFR",  # for now, since we filter by home_type=Houses
        photos=[photo_obj] if photo_obj else [],
    )

    now = datetime.utcnow()

    meta = Meta(
        deal_id=f"zillow-{z.get('zpid')}",
        source="zillow_com1",
        source_id=str(z.get("zpid")),
        created_ts=now,
        updated_ts=now,
    )

    deal = Deal(
        identification=identification,
        acquisition=acquisition,
        physical=physical,
        # financial, reno, valuation, strategy use their defaults
        meta=meta,
    )

    return deal
