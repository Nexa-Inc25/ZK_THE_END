from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = "dev"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://zkflow:zkflow@localhost:5432/zkflow"
    redis_url: str = "redis://localhost:6379/0"

    alchemy_ws_url: Optional[str] = None
    infura_ws_url: Optional[str] = None

    etherscan_api_key: Optional[str] = None
    coingecko_api_base: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: Optional[str] = None

    dune_api_key: Optional[str] = None
    dune_api_base: str = "https://api.dune.com/api/v1"

    nansen_api_key: Optional[str] = None

    alerts_slack_webhook: Optional[str] = None
    alerts_email_smtp_host: Optional[str] = None
    alerts_email_smtp_port: Optional[int] = 587
    alerts_email_username: Optional[str] = None
    alerts_email_password: Optional[str] = None
    alerts_email_from: Optional[str] = None
    alerts_email_to: Optional[str] = None

    threshold_major_usd: float = 50_000_000
    threshold_warning_usd: float = 25_000_000

    # Seed labeled counterparties
    seed_copper_address: Optional[str] = None
    seed_gsr_addr1: Optional[str] = None
    seed_gsr_addr2: Optional[str] = None

    # ZK verifier detection (heuristics)
    verifier_allowlist_csv: Optional[str] = None  # comma-separated addresses
    zk_min_gas_used: int = 400000
    zk_min_calldata: int = 200
    zk_max_calldata: int = 4096


settings = Settings()
