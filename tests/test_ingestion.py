import pandas as pd
import pytest

from src.ingestion.loader import load_transactions
from src.ingestion.schema import RawTransaction


def _make_csv(tmp_path, rows):
    df = pd.DataFrame(rows)
    path = tmp_path / "test.csv"
    df.to_csv(path, index=False)
    return path


def _valid_row(**overrides):
    row = {f"V{i}": 0.1 * i for i in range(1, 29)}
    row.update({"Time": 100.0, "Amount": 25.5, "Class": 0})
    row.update(overrides)
    return row


def test_valid_row_parses(tmp_path):
    path = _make_csv(tmp_path, [_valid_row()])
    result = load_transactions(str(path))
    assert len(result.valid_rows) == 1
    assert len(result.rejected_rows) == 0


def test_invalid_class_is_rejected(tmp_path):
    path = _make_csv(tmp_path, [_valid_row(Class=5)])
    result = load_transactions(str(path))
    assert len(result.valid_rows) == 0
    assert len(result.rejected_rows) == 1


def test_negative_amount_is_rejected(tmp_path):
    path = _make_csv(tmp_path, [_valid_row(Amount=-10.0)])
    result = load_transactions(str(path))
    assert len(result.rejected_rows) == 1


def test_missing_column_raises(tmp_path):
    df = pd.DataFrame([{"Time": 1.0, "Amount": 1.0, "Class": 0}])  # missing V1-V28
    path = tmp_path / "bad.csv"
    df.to_csv(path, index=False)
    with pytest.raises(ValueError):
        load_transactions(str(path))


def test_rejection_rate_computed(tmp_path):
    rows = [_valid_row(), _valid_row(Class=9)]
    path = _make_csv(tmp_path, rows)
    result = load_transactions(str(path))
    assert result.rejection_rate == pytest.approx(0.5)


def test_from_csv_row_builds_v_features():
    row = _valid_row()
    txn = RawTransaction.from_csv_row(row)
    assert len(txn.v_features) == 28
    assert txn.label == 0