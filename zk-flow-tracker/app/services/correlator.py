from typing import List, Dict

# Placeholder correlator; in MVP, correlate by same block_number and window

def correlate(transfers: List[Dict], calls: List[Dict]) -> List[Dict]:
    flows = []
    # naive join by block_number
    calls_by_block = {}
    for c in calls:
        calls_by_block.setdefault(c.get("block_number"), []).append(c)
    for t in transfers:
        block = t.get("block_number")
        suspect = any(c.get("is_verifier_suspect") for c in calls_by_block.get(block, []))
        flows.append({
            "block_number": block,
            "usd_value": t.get("usd_value", 0),
            "verifier_heuristic": suspect,
            "proximity_sec": 0,
            "labeled_counterparty_conf": t.get("labeled_counterparty_conf", 0),
        })
    return flows
