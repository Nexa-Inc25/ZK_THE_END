from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base

class FlowScore(Base):
    __tablename__ = "flow_scores"
    id = Column(Integer, primary_key=True)
    flow_id = Column(Integer, ForeignKey("flows.id"))
    score = Column(Integer)
    explanation = Column(String)

    flow = relationship("Flow")
