import os
import time
import argparse
from decimal import Decimal
from typing import Optional, List
from web3 import Web3
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logger import logger
from app.models.transfer import Transfer
from app.models.token import Token
from app.services.labeling import lookup_label
from app.services.token_registry import get_token_meta
from app.services.enrichment import usd_price_for

ERC20_TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()

class EthereumWatcher:
    def __init__(self, ws_url: Optional[str] = None):
        self.ws_url = ws_url or settings.alchemy_ws_url or settings.infura_ws_url
        if not self.ws_url:
            raise RuntimeError("No WebSocket RPC URL configured.")
        self.w3 = Web3(Web3.WebsocketProvider(self.ws_url))

    def run_once_poll_latest(self, max_events: int = 100):
        latest = self.w3.eth.block_number
        from_block = max(latest - 2, 0)
        to_block = latest
        logs = self.w3.eth.get_logs({
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [ERC20_TRANSFER_TOPIC]
        })
        db = SessionLocal()
        try:
            written = 0
            for lg in logs[:max_events]:
                if self._process_log(lg, db):
                    written += 1
            db.commit()
            return written
        finally:
            db.close()

    def _process_log(self, lg, db) -> bool:
        topics = lg["topics"]
        if not topics or topics[0].hex() != ERC20_TRANSFER_TOPIC:
            return False
        from_addr = "0x" + topics[1].hex()[-40:]
        to_addr = "0x" + topics[2].hex()[-40:]
        token = lg["address"]
        raw_amt = int(lg["data"], 16)
        # Pricing via token registry + CoinGecko
        meta = get_token_meta(token)
        amount_usd = Decimal(0)
        if meta:
            decimals = meta.get("decimals", 18)
            symbol = meta.get("symbol")
            price = usd_price_for(symbol) or 0
            human = Decimal(raw_amt) / (Decimal(10) ** decimals)
            amount_usd = Decimal(price) * human

        lab_from = lookup_label(from_addr)
        lab_to = lookup_label(to_addr)
        labeled_conf = max(
            lab_from["confidence"] if lab_from else 0,
            lab_to["confidence"] if lab_to else 0,
        )
        # Persist only interesting events
        if amount_usd >= Decimal(settings.threshold_warning_usd) or labeled_conf >= 0.7:
            t = Transfer(
                tx_hash=lg["transactionHash"].hex(),
                block_number=lg["blockNumber"],
                chain_id=1,
                from_address=from_addr,
                to_address=to_addr,
                token_address=token,
                raw_amount=raw_amt,
                amount_usd=amount_usd,
            )
            db.add(t)
            return True
        return False

    def _make_log_filter(self):
        return self.w3.eth.filter({
            "fromBlock": "latest",
            "topics": [ERC20_TRANSFER_TOPIC]
        })

    def _make_block_filter(self):
        # 'latest' returns new block hashes when using WS provider
        return self.w3.eth.filter('latest')

    def run_forever_ws(self, poll_interval: float = 0.5, max_per_tick: int = 200):
        backoff = 1.0
        while True:
            try:
                logger.info("starting ws logs loop")
                log_filter = self._make_log_filter()
                blk_filter = self._make_block_filter()
                db = SessionLocal()
                try:
                    while True:
                        wrote = 0
                        # 1) ERC-20 Transfer logs
                        for lg in log_filter.get_new_entries()[:max_per_tick]:
                            if self._process_log(lg, db):
                                wrote += 1
                        # 2) ETH-native transfers via new blocks
                        blk_hashes = blk_filter.get_new_entries()
                        if blk_hashes:
                            # Fetch ETH price once per tick if needed
                            eth_price = usd_price_for("ethereum") or 0
                            for bh in blk_hashes:
                                try:
                                    bn = self.w3.eth.get_block(bh).number if isinstance(bh, bytes) else self.w3.eth.get_block(bh).number
                                    block = self.w3.eth.get_block(bn, full_transactions=True)
                                except Exception:
                                    continue
                                for tx in block.transactions:
                                    to_addr = tx.get('to')
                                    from_addr = tx.get('from')
                                    if not to_addr:
                                        continue  # skip contract creations
                                    wei = int(tx.get('value', 0))
                                    if wei <= 0:
                                        continue
                                    # USD
                                    amount_usd = (Decimal(wei) / Decimal(10**18)) * Decimal(eth_price)
                                    lab_from = lookup_label(from_addr or '')
                                    lab_to = lookup_label(to_addr or '')
                                    labeled_conf = max(
                                        lab_from["confidence"] if lab_from else 0,
                                        lab_to["confidence"] if lab_to else 0,
                                    )
                                    if amount_usd >= Decimal(settings.threshold_warning_usd) or labeled_conf >= 0.7:
                                        t = Transfer(
                                            tx_hash=tx['hash'].hex() if hasattr(tx['hash'], 'hex') else tx['hash'],
                                            block_number=block.number,
                                            chain_id=1,
                                            from_address=from_addr,
                                            to_address=to_addr,
                                            token_address='ETH',
                                            raw_amount=wei,
                                            amount_usd=amount_usd,
                                        )
                                        db.add(t)
                                        wrote += 1
                        if wrote:
                            db.commit()
                        time.sleep(poll_interval)
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"ws loop error: {e}; reconnecting in {backoff:.1f}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, 30.0)
                # Recreate provider on error
                try:
                    self.w3 = Web3(Web3.WebsocketProvider(self.ws_url))
                except Exception:
                    pass
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["poll", "ws"], default="ws")
    parser.add_argument("--interval", type=float, default=0.5, help="Poll interval for ws mode")
    args = parser.parse_args()

    watcher = EthereumWatcher()
    if args.mode == "poll":
        watcher.run_once_poll_latest()
    else:
        watcher.run_forever_ws(poll_interval=args.interval)
