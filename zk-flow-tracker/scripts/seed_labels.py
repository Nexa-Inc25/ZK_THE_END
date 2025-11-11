from app.core.database import SessionLocal, Base, engine
from app.core.config import settings
from app.models.label import Label
from app.models.address import Address

SEEDS = [
    (settings.seed_copper_address, "Copper Custody", 0.8),
    (settings.seed_gsr_addr1, "GSR Trading", 0.8),
    (settings.seed_gsr_addr2, "GSR Trading", 0.8),
]


def get_or_create_label(db, name: str, source: str = "seed", confidence: float = 0.8) -> Label:
    lbl = db.query(Label).filter(Label.name == name).first()
    if lbl:
        return lbl
    lbl = Label(name=name, source=source, confidence=confidence)
    db.add(lbl)
    db.commit()
    db.refresh(lbl)
    return lbl


def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created = 0
        for addr, label_name, conf in SEEDS:
            if not addr:
                continue
            addr = addr.lower()
            lbl = get_or_create_label(db, label_name, confidence=conf)
            existing = db.query(Address).filter(Address.address == addr).first()
            if existing:
                if existing.label_id != lbl.id:
                    existing.label_id = lbl.id
                    existing.confidence = max(existing.confidence or 0.0, conf)
                db.commit()
                continue
            ent = Address(address=addr, label_id=lbl.id, confidence=conf)
            db.add(ent)
            created += 1
        db.commit()
        print(f"Seeded {created} address labels.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
