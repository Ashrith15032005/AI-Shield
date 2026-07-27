"""
Central configuration for AIShield.

Every module pulls config from here instead of reading os.environ directly.
This is the single source of truth for paths, model params, and service settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = two levels up from this file (configs/settings.py -> AIShield/)
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App metadata ---
    app_name: str = "AIShield"
    environment: str = "dev"  # dev | staging | prod
    log_level: str = "INFO"

    # --- Paths ---
    data_raw_dir: Path = ROOT_DIR / "data" / "raw"
    data_processed_dir: Path = ROOT_DIR / "data" / "processed"
    data_validated_dir: Path = ROOT_DIR / "data" / "validated"
    data_features_dir: Path = ROOT_DIR / "data" / "features"
    data_drift_dir: Path = ROOT_DIR / "data" / "drift"
    models_dir: Path = ROOT_DIR / "models"

    # --- Feature store (Phase 1: flat parquet file; swapped for Feast later) ---
    feature_store_path: Path = ROOT_DIR / "feature_store" / "features.parquet"

    # --- MLflow ---
    mlflow_tracking_uri: str = f"file://{ROOT_DIR / 'mlflow' / 'mlruns'}"
    mlflow_experiment_name: str = "aishield-fraud-detection"
    mlflow_registered_model_name: str = "aishield-fraud-model"

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- Auth (Phase 4) ---
    jwt_secret_key: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # --- Training ---
    random_seed: int = 42
    test_size: float = 0.2


settings = Settings()
