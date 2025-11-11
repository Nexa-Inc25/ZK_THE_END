# zk-flow-tracker (Crypto ZK Dark Pool Tracker MVP)

MVP backend and internal dashboard to detect and score high-value settlement flows possibly related to ZK dark pool activity on Ethereum L1.

## Features (MVP)
- FastAPI API server (events, flows, alerts)
- Postgres (storage) + Redis (cache/dedupe)
- Ethereum watcher (ERC-20 transfers), correlation & scoring
- Slack/Email alert stubs
- Streamlit dashboard for internal use

## Quickstart
1. Copy env and fill values
```bash
cp .env.example .env
```

2. Start infra (Postgres, Redis)
```bash
docker compose up -d db redis
```

3. Create venv and install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Initialize DB (automatic on first API start), seed labels (optional)
```bash
uvicorn app.main:app --reload
python scripts/seed_labels.py
```

5. Run Streamlit UI
```bash
streamlit run streamlit/App.py
```

## Environment
- See `.env.example` for required variables (Alchemy/Infura WS, Postgres, Redis, Etherscan, CoinGecko, Slack webhook).

## Notes
- Websocket watcher focuses on ERC-20 `Transfer` events and applies thresholds ($50M major, $10M warning) with basic correlation heuristics.
- Verifier contract allowlist hooks are provided but empty by default.
