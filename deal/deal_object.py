# deal/deal_object.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Identification(BaseModel):
    address_full: str
    street: Optional[str] = None
    city: str
    state: str
    zip: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    parcel_id: Optional[str] = None


class Acquisition(BaseModel):
    list_price: Optional[float] = None
    estimated_entry_price: Optional[float] = None
    source: Optional[str] = None  # realtor_api, off_market, mls_manual, etc.
    status: Optional[str] = None  # active, pending, sold, off_market (normalized later)
    days_on_market: Optional[int] = None
    last_update_ts: Optional[datetime] = None


class Photo(BaseModel):
    url: str
    label: Optional[str] = None  # front, kitchen, etc.


class Physical(BaseModel):
    beds: Optional[float] = None  # sometimes 2.5 etc.
    baths: Optional[float] = None
    sqft: Optional[int] = None
    year_built: Optional[int] = None
    lot_sqft: Optional[int] = None
    property_type: Optional[str] = None  # SFR, condo, duplex, etc.
    stories: Optional[float] = None
    parking_type: Optional[str] = None
    photos: List[Photo] = Field(default_factory=list)


class Financial(BaseModel):
    tax_annual: Optional[float] = None
    tax_assessed_value: Optional[float] = None
    hoa_monthly: Optional[float] = None
    insurance_est_monthly: Optional[float] = None
    current_rent_monthly: Optional[float] = None


class RenoScopeItem(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    labor_cost: Optional[float] = None
    materials_cost: Optional[float] = None
    total_cost: Optional[float] = None
    duration_days: Optional[int] = None
    confidence: Optional[float] = None  # 0–1


class Reno(BaseModel):
    scope_items: List[RenoScopeItem] = Field(default_factory=list)
    total_cost: Optional[float] = None
    total_duration_days: Optional[int] = None
    contingency_pct: Optional[float] = None  # 0–1


class Comp(BaseModel):
    comp_id: Optional[str] = None
    address: Optional[str] = None
    distance_miles: Optional[float] = None
    close_price: Optional[float] = None
    close_date: Optional[datetime] = None
    sqft: Optional[int] = None
    beds: Optional[float] = None
    baths: Optional[float] = None
    adjusted_price: Optional[float] = None


class Valuation(BaseModel):
    arv_estimate: Optional[float] = None
    arv_low: Optional[float] = None
    arv_high: Optional[float] = None
    arv_confidence: Optional[float] = None
    comp_set: List[Comp] = Field(default_factory=list)


class Strategy(BaseModel):
    preferred_strategy: Optional[Literal["flip", "hold", "wholesale"]] = None
    target_hold_months: Optional[int] = None
    target_irr: Optional[float] = None  # 0.25 = 25%
    downside_flat_market_roi: Optional[float] = None
    downside_minus10_pct_market_roi: Optional[float] = None


class Meta(BaseModel):
    deal_id: str  # internal ID, e.g. "DAL-75206-123456"
    source: Optional[str] = None      # realtor_api, etc.
    source_id: Optional[str] = None   # listing_id from Realtor, etc.
    created_ts: datetime
    updated_ts: datetime
    version: int = 1


class Deal(BaseModel):
    identification: Identification
    acquisition: Acquisition
    physical: Physical
    financial: Financial = Field(default_factory=Financial)
    reno: Reno = Field(default_factory=Reno)
    valuation: Valuation = Field(default_factory=Valuation)
    strategy: Strategy = Field(default_factory=Strategy)
    meta: Meta

    # ---- Convenience computed properties ----
    @property
    def price_per_sqft(self) -> Optional[float]:
        if self.acquisition.list_price and self.physical.sqft:
            return self.acquisition.list_price / self.physical.sqft
        return None

    # ---- Example constructor from a Realtor listing dict ----
    @classmethod
    def from_realtor(cls, listing: dict) -> "Deal":
        """
        Thin v0 mapping from a Realtor API listing payload → Deal.
        You will refine this to match your exact Realtor response shape.
        """
        loc = listing.get("location", {}).get("address", {})
        desc = listing.get("description", {})
        lot = listing.get("lot_size", {})

        now = datetime.utcnow()

        identification = Identification(
            address_full=loc.get("line", ""),
            street=loc.get("line", ""),
            city=loc.get("city", ""),
            state=loc.get("state_code", ""),
            zip=loc.get("postal_code", ""),
            lat=(loc.get("coordinate", {}) or {}).get("lat"),
            lon=(loc.get("coordinate", {}) or {}).get("lon"),
            parcel_id=None,  # filled later by assessor match
        )

        acquisition = Acquisition(
            list_price=listing.get("list_price"),
            estimated_entry_price=listing.get("list_price"),
            source="realtor_api",
            status=listing.get("status"),
            days_on_market=listing.get("days_on_market"),
            last_update_ts=listing.get("last_update"),
        )

        photos = [
            Photo(url=p.get("href"), label=None)
            for p in listing.get("photos", []) if p.get("href")
        ]

        physical = Physical(
            beds=desc.get("beds"),
            baths=desc.get("baths"),
            sqft=desc.get("sqft"),
            year_built=desc.get("year_built"),
            lot_sqft=lot.get("size"),
            property_type=desc.get("type"),
            stories=desc.get("stories"),
            parking_type=desc.get("garage_type"),
            photos=photos,
        )

        meta = Meta(
            deal_id=f"realtor-{listing.get('listing_id')}",
            source="realtor_api",
            source_id=str(listing.get("listing_id")),
            created_ts=now,
            updated_ts=now,
        )

        return cls(
            identification=identification,
            acquisition=acquisition,
            physical=physical,
            financial=Financial(),
            reno=Reno(),
            valuation=Valuation(),
            strategy=Strategy(preferred_strategy="flip"),
            meta=meta,
        )
