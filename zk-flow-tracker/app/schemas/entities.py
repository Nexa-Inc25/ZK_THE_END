from pydantic import BaseModel
from typing import Optional

class FlowOut(BaseModel):
    id: int
    block_number: int
    chain_id: int
    usd_value: float
    labeled_counterparty_conf: float
    verifier_allowlist: bool
    verifier_heuristic: bool
    proximity_sec: int
    summary: Optional[str] = None

    class Config:
        from_attributes = True

class TransferOut(BaseModel):
    id: int
    tx_hash: str
    block_number: int
    chain_id: int
    from_address: str
    to_address: str
    token_address: str
    amount_usd: float

    class Config:
        from_attributes = True
