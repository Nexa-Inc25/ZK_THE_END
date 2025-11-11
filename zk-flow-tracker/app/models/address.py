from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Address(Base):
    __tablename__ = "addresses"
    address = Column(String, primary_key=True, index=True)
    label_id = Column(Integer, ForeignKey("labels.id"), nullable=True)
    cluster_id = Column(String, nullable=True)
    confidence = Column(Float, default=0.5)

    label = relationship("Label")
