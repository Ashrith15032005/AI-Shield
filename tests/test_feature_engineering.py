import math

import pytest

from src.feature_engineering.transform import transform, transform_batch
from src.ingestion.augment import augment_transactions
from src.ingestion.schema import RawTransaction


def _make_txn(time=100.0, amount=25.5, label=0):
    return RawTransaction(
        time=time,
        v_features=[0.1 * i for i in range(1, 29)],
        amount=amount,
        label=label,
    )


def test_augmentation_is_deterministic():
    txn = _make_txn()
    aug1 = augment_transactions([txn])[0]
    aug2 = augment_transactions([txn])[0]
    assert aug1.merchant_category == aug2.merchant_category
    assert aug1.device_type == aug2.device_type
    assert aug1.account_age_days == aug2.account_age_days


def test_transaction_hour_derivation():
    txn = _make_txn(time=3600 * 5)  # 5 hours in
    aug = augment_transactions([txn])[0]
    assert aug.transaction_hour == 5


def test_transform_produces_expected_keys():
    txn = _make_txn()
    aug = augment_transactions([txn])[0]
    features = transform(aug)

    assert "amount_log" in features
    assert features["amount_log"] == math.log1p(25.5)
    assert "hour_sin" in features and "hour_cos" in features
    assert sum(v for k, v in features.items() if k.startswith("merchant_")) == 1
    assert sum(v for k, v in features.items() if k.startswith("device_")) == 1
    assert sum(v for k, v in features.items() if k.startswith("account_age_")) == 1
    assert features["label"] == 0


def test_v_features_passthrough():
    txn = _make_txn()
    aug = augment_transactions([txn])[0]
    features = transform(aug)
    assert features["v1"] == 0.1
    assert features["v28"] == pytest.approx(2.8)


def test_transform_batch_length_matches_input():
    txns = [_make_txn(time=t) for t in [0, 3600, 7200]]
    augmented = augment_transactions(txns)
    features = transform_batch(augmented)
    assert len(features) == 3