def score_flow(flow_features: dict) -> tuple[int, str]:
    score = 0
    expl = []

    conf = flow_features.get("labeled_counterparty_conf", 0)
    if conf >= 0.7:
        score += 35
        expl.append("labeled_counterparty")

    if flow_features.get("verifier_allowlist"):
        score += 25
        expl.append("verifier_allowlist")

    # ZK-specific signals
    if flow_features.get("trace_bn256"):
        score += 20
        expl.append("trace_bn256")

    if flow_features.get("verifier_heuristic") and flow_features.get("proximity_sec", 9999) <= 60:
        score += 15
        expl.append("verifier_heuristic_proximity")

    # Value tiers
    usd = float(flow_features.get("usd_value", 0) or 0)
    if usd >= 50_000_000:
        score += 15
        expl.append("value_50m+")
    elif usd >= 25_000_000:
        score += 10
        expl.append("value_25m+")
    elif usd >= 10_000_000:
        score += 5
        expl.append("value_10m+")

    # ETH-native bonus
    if flow_features.get("is_eth_native"):
        score += 10
        expl.append("eth_native")

    if flow_features.get("benign_pattern"):
        score -= 10
        expl.append("benign_pattern")

    return min(score, 100), ",".join(expl)
