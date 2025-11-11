# Minimal Ethereum mainnet token registry for MVP pricing
# Addresses are checksummed lower-case for matching
TOKEN_REGISTRY = {
    # USDC
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {"symbol": "usd-coin", "decimals": 6},
    # USDT
    "0xdac17f958d2ee523a2206206994597c13d831ec7": {"symbol": "tether", "decimals": 6},
    # DAI
    "0x6b175474e89094c44da98b954eedeac495271d0f": {"symbol": "dai", "decimals": 18},
    # WETH
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {"symbol": "weth", "decimals": 18},
}

def get_token_meta(address: str):
    if not address:
        return None
    return TOKEN_REGISTRY.get(address.lower())
