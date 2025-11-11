from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Numeric, DateTime
from sqlalchemy.sql import func
from .base import Base

class Flow(Base):
    __tablename__ = "flows"
    id = Column(Integer, primary_key=True)
    block_number = Column(BigInteger, index=True)
    block_time = Column(DateTime(timezone=True), server_default=func.now())
    chain_id = Column(Integer, default=1)
    usd_value = Column(Numeric(38,2))
    labeled_counterparty_conf = Column(Numeric(5,2), default=0)
    verifier_allowlist = Column(Boolean, default=False)
    verifier_heuristic = Column(Boolean, default=False)
    proximity_sec = Column(Integer, default=0)
    summary = Column(String)
