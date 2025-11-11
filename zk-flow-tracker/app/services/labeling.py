from typing import Optional, Dict
from app.core.config import settings

SEED_LABELS: Dict[str, Dict] = {}

# Seed known entities if provided via env
for env_key, label_name in [
    ("SEED_COPPER_ADDRESS", "Copper Custody"),
    ("SEED_GSR_ADDR1", "GSR Trading"),
    ("SEED_GSR_ADDR2", "GSR Trading"),
]:
    addr = getattr(settings, env_key.lower(), None) if hasattr(settings, env_key.lower()) else None
    if not addr:
        addr = None
    # Fallback to reading raw env if not modeled
    if not addr:
        import os
        addr = os.getenv(env_key)
    if addr:
        SEED_LABELS[addr.lower()] = {"label": label_name, "confidence": 0.8}


def lookup_label(address: str) -> Optional[Dict]:
    return SEED_LABELS.get(address.lower())
