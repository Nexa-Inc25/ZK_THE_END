from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Float
from .base import Base

class ContractCall(Base):
    __tablename__ = "contract_calls"
    id = Column(Integer, primary_key=True)
    tx_hash = Column(String, index=True, nullable=False)
    to_address = Column(String, index=True)
    selector = Column(String, index=True)
    gas_used = Column(BigInteger)
    calldata_len = Column(Integer)
    is_verifier_suspect = Column(Boolean, default=False)
    # Allowlist enrichment
    is_allowlisted = Column(Boolean, default=False)
    allowlist_protocol = Column(String)
    allowlist_confidence = Column(Float)
    # Trace-based
    uses_bn256_pairing = Column(Boolean, default=False)

    block_number = Column(BigInteger, index=True)
