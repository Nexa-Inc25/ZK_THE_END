import argparse
from typing import Optional
from web3 import Web3
from app.core.config import settings
from app.core.database import SessionLocal, Base, engine
from app.core.logger import logger
from app.models.contract_call import ContractCall
from app.services.zk_verifier import (
    is_allowlisted,
    is_suspect_call,
    allowlist_info,
    trace_uses_bn256_pairing,
)


def get_w3() -> Web3:
    ws = settings.alchemy_ws_url or settings.infura_ws_url
    if not ws:
        raise RuntimeError("No RPC URL configured (ALCHEMY_WS_URL or INFURA_WS_URL)")
    return Web3(Web3.WebsocketProvider(ws))


def scan_range(from_block: int, to_block: int) -> int:
    w3 = get_w3()
    db = SessionLocal()
    created = 0
    try:
        for bn in range(from_block, to_block + 1):
            block = w3.eth.get_block(bn, full_transactions=True)
            for tx in block.transactions:
                to = tx["to"]
                # Only consider contract calls (to != None)
                if not to:
                    continue
                tx_hash = tx["hash"].hex()
                # dedupe by tx_hash
                if db.query(ContractCall).filter(ContractCall.tx_hash == tx_hash).first():
                    continue
                try:
                    receipt = w3.eth.get_transaction_receipt(tx_hash)
                    gas_used = receipt["gasUsed"]
                except Exception as e:
                    logger.warning(f"receipt fetch failed {tx_hash}: {e}")
                    continue
                input_hex = tx["input"].hex() if hasattr(tx["input"], "hex") else tx["input"]
                allow = is_allowlisted(to)
                info = allowlist_info(to)
                suspect = is_suspect_call(input_hex, gas_used)
                uses_bn256 = False
                # Attempt trace; provider may not support debug methods
                try:
                    trace = w3.manager.request_blocking(
                        "debug_traceTransaction", [tx_hash, {"tracer": "callTracer"}]
                    )
                    uses_bn256 = trace_uses_bn256_pairing(trace)
                except Exception:
                    uses_bn256 = False
                if allow or suspect or uses_bn256:
                    rec = ContractCall(
                        tx_hash=tx_hash,
                        to_address=to,
                        selector=input_hex[:10] if input_hex and input_hex.startswith("0x") else None,
                        gas_used=gas_used,
                        calldata_len=max((len(input_hex) - 2) // 2, 0) if input_hex else 0,
                        is_verifier_suspect=bool(suspect or allow or uses_bn256),
                        is_allowlisted=bool(allow),
                        allowlist_protocol=(info or {}).get("protocol"),
                        allowlist_confidence=(info or {}).get("confidence"),
                        uses_bn256_pairing=bool(uses_bn256),
                        block_number=bn,
                    )
                    db.add(rec)
                    created += 1
            if created:
                db.commit()
    finally:
        db.close()
    return created


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-block", type=int)
    parser.add_argument("--to-block", type=int)
    parser.add_argument("--range", type=int, default=5, help="Scan last N blocks if from/to not provided")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    w3 = get_w3()
    latest = w3.eth.block_number
    if args.from_block is not None and args.to_block is not None:
        fr, to = args.from_block, args.to_block
    else:
        to = latest
        fr = max(latest - args.range + 1, 0)

    logger.info(f"scanning blocks {fr}..{to}")
    created = scan_range(fr, to)
    logger.info(f"created {created} contract_call rows")


if __name__ == "__main__":
    main()
