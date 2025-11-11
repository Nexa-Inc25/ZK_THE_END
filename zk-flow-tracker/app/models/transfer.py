from sqlalchemy import Column, Integer, String, BigInteger, Numeric, DateTime
from sqlalchemy.sql import func
from .base import Base

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    tx_hash = Column(String, index=True, nullable=False)
    block_number = Column(BigInteger, index=True)
    block_time = Column(DateTime(timezone=True), server_default=func.now())
    chain_id = Column(Integer, default=1)
    from_address = Column(String, index=True)
    to_address = Column(String, index=True)
    token_address = Column(String, index=True)
    raw_amount = Column(BigInteger)
    amount_usd = Column(Numeric(38, 2))
