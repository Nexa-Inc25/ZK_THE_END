from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.database import Base, engine, get_db
from app.api.routes import router as api_router
from app.models import (
    address as _m_address,
    label as _m_label,
    token as _m_token,
    transfer as _m_transfer,
    contract_call as _m_contract_call,
    flow as _m_flow,
    flow_score as _m_flow_score,
    alert as _m_alert,
)

app = FastAPI(title="zk-flow-tracker API", version="0.1.0")

# Create tables on startup for MVP
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api")
