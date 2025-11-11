from typing import Optional, Set, Dict, Any
from app.core.config import settings

_allowlist_map: Optional[Dict[str, Dict[str, Any]] ] = None


def _load_allowlist_map() -> Dict[str, Dict[str, Any]]:
    """
    Supports formats:
    - 
      VERIFIER_ALLOWLIST_CSV="0xabc...,GoDark,0.9;0xdef...,Renegade,0.8"
    - or simple address list:
      VERIFIER_ALLOWLIST_CSV="0xabc...,0xdef..."
    """
    global _allowlist_map
    if _allowlist_map is not None:
        return _allowlist_map
    raw = (settings.verifier_allowlist_csv or "").strip()
    m: Dict[str, Dict[str, Any]] = {}
    if raw:
        # normalize record separators to ';'
        normalized = raw.replace("\n", ";")
        records = [r.strip() for r in normalized.split(";") if r.strip()]
        if records:
            for rec in records:
                parts = [p.strip() for p in rec.split(",") if p.strip()]
                if not parts:
                    continue
                addr = parts[0].lower()
                protocol = parts[1] if len(parts) > 1 else None
                conf = None
                if len(parts) > 2:
                    try:
                        conf = float(parts[2])
                    except Exception:
                        conf = None
                m[addr] = {"protocol": protocol, "confidence": conf}
        else:
            for a in [x.strip() for x in raw.split(",") if x.strip()]:
                m[a.lower()] = {"protocol": None, "confidence": None}
    _allowlist_map = m
    return _allowlist_map


def is_allowlisted(address: Optional[str]) -> bool:
    if not address:
        return False
    return address.lower() in _load_allowlist_map()


def allowlist_info(address: Optional[str]) -> Optional[Dict[str, Any]]:
    if not address:
        return None
    return _load_allowlist_map().get(address.lower())


def is_suspect_call(input_hex: str, gas_used: int) -> bool:
    if not input_hex or not input_hex.startswith("0x"):
        return False
    calldata_len = max((len(input_hex) - 2) // 2, 0)
    if gas_used < settings.zk_min_gas_used:
        return False
    if calldata_len < settings.zk_min_calldata or calldata_len > settings.zk_max_calldata:
        return False
    return True


def trace_uses_bn256_pairing(trace_root: Dict[str, Any]) -> bool:
    """Walk callTracer JSON to detect BN256 pairing precompile (0x08)."""
    def walk(node: Dict[str, Any]) -> bool:
        to = (node.get("to") or "").lower()
        if to.endswith("0000000000000000000000000000000000000008") or to == "0x08":
            return True
        for c in node.get("calls", []) or []:
            if walk(c):
                return True
        return False
    try:
        return walk(trace_root)
    except Exception:
        return False
