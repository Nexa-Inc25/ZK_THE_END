from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    flow_id = Column(Integer, ForeignKey("flows.id"))
    channel = Column(String)
    status = Column(String, default="queued")
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    dedupe_key = Column(String, index=True)

    flow = relationship("Flow")
