from sqlalchemy import Column, Integer, String, Float
from .base import Base

class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    source = Column(String, nullable=True)
    confidence = Column(Float, default=0.5)
