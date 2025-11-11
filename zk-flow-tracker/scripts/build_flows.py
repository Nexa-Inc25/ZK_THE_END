from decimal import Decimal
from app.core.database import SessionLocal
from app.models.transfer import Transfer
from app.models.flow import Flow
from app.models.flow_score import FlowScore
from app.services.labeling import lookup_label
from app.services.scoring import score_flow
from app.services.alerts import notify_flow
from app.core.config import settings
from app.models.contract_call import ContractCall
from app.services.zk_verifier import is_allowlisted

LIMIT = 200


def flow_summary_from_transfer(t: Transfer) -> str:
    return f"tx:{t.tx_hash} usd:{t.amount_usd} from:{t.from_address} to:{t.to_address}"


def main():
    db = SessionLocal()
    created = 0
    try:
        transfers = (
            db.query(Transfer)
            .order_by(Transfer.id.desc())
            .limit(LIMIT)
            .all()
        )
        for t in reversed(transfers):
            # dedupe: skip if a flow with same summary exists
            summary = flow_summary_from_transfer(t)
            exists = db.query(Flow).filter(Flow.summary == summary).first()
            if exists:
                continue

            lab_from = lookup_label(t.from_address or "")
            lab_to = lookup_label(t.to_address or "")
            labeled_conf = max(
                (lab_from or {}).get("confidence", 0),
                (lab_to or {}).get("confidence", 0),
            )

            # correlate with contract calls in same block
            calls = db.query(ContractCall).filter(ContractCall.block_number == t.block_number).all()
            has_allow = any(getattr(c, 'is_allowlisted', False) for c in calls) or any(is_allowlisted(c.to_address) for c in calls)
            has_suspect = any(getattr(c, 'is_verifier_suspect', False) for c in calls)
            has_bn256 = any(getattr(c, 'uses_bn256_pairing', False) for c in calls)

            is_eth_native = (t.token_address == 'ETH')

            features = {
                "usd_value": float(t.amount_usd or 0),
                "labeled_counterparty_conf": labeled_conf,
                "verifier_allowlist": has_allow,
                "verifier_heuristic": has_suspect,
                "trace_bn256": has_bn256,
                "is_eth_native": is_eth_native,
                "proximity_sec": 0,
            }
            score, expl = score_flow(features)

            flow = Flow(
                block_number=t.block_number,
                chain_id=t.chain_id,
                usd_value=t.amount_usd,
                labeled_counterparty_conf=labeled_conf,
                verifier_allowlist=has_allow,
                verifier_heuristic=has_suspect,
                proximity_sec=0,
                summary=summary,
            )
            db.add(flow)
            db.flush()
            fs = FlowScore(flow_id=flow.id, score=score, explanation=expl)
            db.add(fs)
            created += 1

            # Notify if score is high
            if score >= 70:
                notify_flow(f"Flow score {score}: {summary}")

        db.commit()
        print(f"Created {created} flows from recent transfers.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
