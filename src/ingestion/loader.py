"""CSV ingestion: load raw transactions with row-level schema validation."""

import logging
from dataclasses import dataclass, field

import pandas as pd
from pydantic import ValidationError

from src.ingestion.schema import RawTransaction

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [f"V{i}" for i in range(1, 29)] + ["Time", "Amount", "Class"]


@dataclass
class IngestionResult:
    """Outcome of loading a CSV: valid rows plus any rejected rows."""

    valid_rows: list[RawTransaction] = field(default_factory=list)
    rejected_rows: list[dict] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.valid_rows) + len(self.rejected_rows)

    @property
    def rejection_rate(self) -> float:
        return len(self.rejected_rows) / self.total if self.total else 0.0


def load_transactions(csv_path: str) -> IngestionResult:
    """Load a CSV file, validating each row against RawTransaction.

    Rows that fail validation are collected separately rather than
    crashing the whole ingestion run — bad data is common in production
    and should be quarantined, not silently dropped or fatal.
    """
    df = pd.read_csv(csv_path)

    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV missing required columns: {sorted(missing_cols)}")

    result = IngestionResult()
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        try:
            txn = RawTransaction.from_csv_row(row_dict)
            result.valid_rows.append(txn)
        except (ValidationError, ValueError, KeyError) as exc:
            logger.warning("Rejected row: %s", exc)
            result.rejected_rows.append(row_dict)

    logger.info(
        "Ingested %d rows: %d valid, %d rejected (%.2f%% rejection rate)",
        result.total,
        len(result.valid_rows),
        len(result.rejected_rows),
        result.rejection_rate * 100,
    )
    return result