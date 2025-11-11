from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.flow import Flow
from app.models.transfer import Transfer
from app.schemas.entities import FlowOut, TransferOut

router = APIRouter()

@router.get("/flows", response_model=List[FlowOut])
def list_flows(limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Flow).order_by(Flow.id.desc()).limit(limit)
    return q.all()

@router.get("/events/transfers", response_model=List[TransferOut])
def list_transfers(limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Transfer).order_by(Transfer.id.desc()).limit(limit)
    return q.all()
