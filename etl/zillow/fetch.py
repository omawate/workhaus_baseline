# etl/zillow/fetch.py

import os
import time
import logging
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
BASE_HOST = "zillow-com1.p.rapidapi.com"

# Env-driven defaults, can be overridden per call
ZILLOW_DEFAULT_LOCATION = os.getenv("ZILLOW_DEFAULT_LOCATION", "Barnstable County, MA")
ZILLOW_DEFAULT_PRICE_MIN = int(os.getenv("ZILLOW_PRICE_MIN", "150000"))
ZILLOW_DEFAULT_PRICE_MAX = int(os.getenv("ZILLOW_PRICE_MAX", "800000"))
ZILLOW_DEFAULT_BEDS_MIN = int(os.getenv("ZILLOW_BEDS_MIN", "2"))


def _get_headers() -> Dict[str, str]:
    if not RAPIDAPI_KEY:
        raise ValueError("RAPIDAPI_KEY is not set in environment variables.")
    return {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": BASE_HOST,
    }


def zillow_search_by_location(
    location: str,
    price_min: int,
    price_max: int,
    beds_min: int,
    home_type: str = "Houses",
    retries: int = 3,
    sleep_between_retries: float = 1.0,
) -> List[Dict]:
    """
    Call /propertyExtendedSearch using a human-readable location string.

    Example:
      location="Barnstable County, MA"
    """
    url = f"https://{BASE_HOST}/propertyExtendedSearch"
    headers = _get_headers()

    params = {
        "location": location,
        "price_min": price_min,
        "price_max": price_max,
        "beds_min": beds_min,
        "home_type": home_type,
        "sort": "lowestprice",
    }

    last_exc: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                f"[Zillow] propertyExtendedSearch location='{location}', "
                f"price_min={price_min}, price_max={price_max}, beds_min={beds_min} "
                f"(attempt {attempt}/{retries})"
            )
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"[Zillow] propertyExtendedSearch raw type={type(data)}")

            # Normalize different response shapes to a list of properties
            if isinstance(data, list):
                props = data
            elif isinstance(data, dict):
                if "props" in data:
                    props = data["props"]
                elif "results" in data:
                    props = data["results"]
                else:
                    raise ValueError(
                        f"Unexpected propertyExtendedSearch dict structure: {data}"
                    )
            else:
                raise ValueError(
                    f"Unexpected propertyExtendedSearch response type: {type(data)}, value={data}"
                )

            if not isinstance(props, list):
                raise ValueError(f"'props' is not a list: {props}")

            logger.info(f"[Zillow] Received {len(props)} properties.")
            return props

        except Exception as e:
            logger.warning(f"[Zillow] Search failed on attempt {attempt}: {e}")
            last_exc = e
            if attempt < retries:
                time.sleep(sleep_between_retries)

    if last_exc is not None:
        raise last_exc
    return []


def fetch_zillow_listings(
    location_query: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    beds_min: Optional[int] = None,
) -> List[Dict]:
    """
    High-level entry point for Workhaus.

    Uses a human-readable location (no regionId):
      - location_query: e.g. 'Barnstable County, MA', 'Cape Cod, MA', 'Austin, TX'
    """
    loc = location_query or ZILLOW_DEFAULT_LOCATION
    pmin = price_min if price_min is not None else ZILLOW_DEFAULT_PRICE_MIN
    pmax = price_max if price_max is not None else ZILLOW_DEFAULT_PRICE_MAX
    bmin = beds_min if beds_min is not None else ZILLOW_DEFAULT_BEDS_MIN

    logger.info(
        f"[Zillow] Fetching listings for '{loc}' "
        f"(price_min={pmin}, price_max={pmax}, beds_min={bmin})"
    )

    return zillow_search_by_location(
        location=loc,
        price_min=pmin,
        price_max=pmax,
        beds_min=bmin,
    )
