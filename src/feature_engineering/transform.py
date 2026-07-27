"""Feature engineering: raw + augmented transaction -> model-ready feature row.

Transform choices:
  - Amount: log1p transform (fraud amounts are heavy-tailed).
  - transaction_hour: cyclical sin/cos encoding (hour 23 and hour 0 are adjacent).
  - merchant_category / device_type: one-hot encoded against a fixed vocabulary,
    so the output schema is stable regardless of what appears in a given batch.
  - account_age_days: bucketed into risk-relevant tiers.
  - v_features: passed through unchanged (already PCA-decorrelated).
"""

import math

from src.ingestion.augment import AugmentedTransaction, DEVICE_TYPES, MERCHANT_CATEGORIES

ACCOUNT_AGE_BUCKETS = [
    ("new", 0, 30),
    ("recent", 30, 180),
    ("established", 180, 730),
    ("long_standing", 730, float("inf")),
]


def _bucket_account_age(days: int) -> str:
    for name, lo, hi in ACCOUNT_AGE_BUCKETS:
        if lo <= days < hi:
            return name
    return "long_standing"


def transform(txn: AugmentedTransaction) -> dict:
    features: dict = {}

    for i, v in enumerate(txn.raw.v_features, start=1):
        features[f"v{i}"] = v

    features["amount_log"] = math.log1p(txn.raw.amount)

    hour_angle = 2 * math.pi * txn.transaction_hour / 24
    features["hour_sin"] = math.sin(hour_angle)
    features["hour_cos"] = math.cos(hour_angle)

    for cat in MERCHANT_CATEGORIES:
        features[f"merchant_{cat}"] = int(txn.merchant_category == cat)

    for dev in DEVICE_TYPES:
        features[f"device_{dev}"] = int(txn.device_type == dev)

    age_bucket = _bucket_account_age(txn.account_age_days)
    for name, _, _ in ACCOUNT_AGE_BUCKETS:
        features[f"account_age_{name}"] = int(age_bucket == name)

    features["label"] = txn.raw.label
    return features


def transform_batch(transactions: list[AugmentedTransaction]) -> list[dict]:
    return [transform(txn) for txn in transactions]