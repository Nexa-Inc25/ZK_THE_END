from sqlalchemy import Column, String, Integer
from .base import Base

class Token(Base):
    __tablename__ = "tokens"
    address = Column(String, primary_key=True)
    symbol = Column(String, index=True)
    decimals = Column(Integer, default=18)
    chain_id = Column(Integer, default=1)
