from datetime import datetime, timedelta
import requests
from typing import Optional
from app.core.config import settings

COINGECKO_SIMPLE_PRICE = "/simple/price"

_PRICE_CACHE = {}
_TTL = timedelta(seconds=60)


def usd_price_for(symbol: str, coingecko_base: str | None = None) -> Optional[float]:
    base = coingecko_base or settings.coingecko_api_base
    key = symbol.lower()
    now = datetime.utcnow()
    ent = _PRICE_CACHE.get(key)
    if ent and now - ent[1] < _TTL:
        return ent[0]
    try:
        headers = {}
        if settings.coingecko_api_key:
            # CoinGecko Pro header name
            headers["x-cg-pro-api-key"] = settings.coingecko_api_key
        r = requests.get(
            f"{base}{COINGECKO_SIMPLE_PRICE}",
            params={"ids": key, "vs_currencies": "usd"},
            timeout=5,
            headers=headers,
        )
        js = r.json()
        price = float(js[key]["usd"]) if key in js else None
        if price is not None:
            _PRICE_CACHE[key] = (price, now)
        return price
    except Exception:
        return None
