"""Augment ULB's anonymized transactions with deterministic synthetic raw fields.

The source dataset's V1-V28 are already PCA-anonymized, so there's no real
merchant/device/customer metadata to engineer features from. This module
simulates what a fraud platform would typically receive from upstream
services (merchant catalog, device fingerprinting, customer profile) so the
feature engineering step has genuine raw-to-feature transform logic to
perform, rather than passthrough of pre-processed columns.

Derivation is deterministic (hash-seeded per row) so pipeline runs are
reproducible, not randomly regenerated on every execution.
"""

import hashlib

from src.ingestion.schema import RawTransaction

MERCHANT_CATEGORIES = [
    "grocery",
    "electronics",
    "travel",
    "dining",
    "fuel",
    "online_retail",
    "utilities",
    "entertainment",
]
DEVICE_TYPES = ["mobile_ios", "mobile_android", "desktop_web", "pos_terminal"]

SECONDS_PER_DAY = 86400


def _row_seed(txn: RawTransaction) -> int:
    """Deterministic seed derived from the row's own values (no external index needed)."""
    key = f"{txn.time}:{txn.amount}:{txn.v_features[0]}"
    return int(hashlib.sha256(key.encode()).hexdigest(), 16)


class AugmentedTransaction:  # pylint: disable=too-few-public-methods
    """A RawTransaction plus synthesized upstream-service fields."""

    def __init__(self, txn: RawTransaction):
        seed = _row_seed(txn)
        self.raw = txn
        self.transaction_hour = int(txn.time % SECONDS_PER_DAY) // 3600
        self.merchant_category = MERCHANT_CATEGORIES[seed % len(MERCHANT_CATEGORIES)]
        self.device_type = DEVICE_TYPES[(seed // 7) % len(DEVICE_TYPES)]
        # account_age_days: skew toward established accounts (realistic base rate),
        # but keep a long tail of very new accounts (higher fraud correlation).
        self.account_age_days = 1 + ((seed // 13) % 2000)

    def to_dict(self) -> dict:
        return {
            "time": self.raw.time,
            "amount": self.raw.amount,
            "v_features": self.raw.v_features,
            "label": self.raw.label,
            "transaction_hour": self.transaction_hour,
            "merchant_category": self.merchant_category,
            "device_type": self.device_type,
            "account_age_days": self.account_age_days,
        }


def augment_transactions(transactions: list[RawTransaction]) -> list[AugmentedTransaction]:
    return [AugmentedTransaction(txn) for txn in transactions]