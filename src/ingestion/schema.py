"""Pydantic schemas for raw transaction ingestion.

Validates each row of the source CSV against the expected ULB
Credit Card Fraud Detection schema before it enters the pipeline.
"""

from pydantic import BaseModel, Field, field_validator


class RawTransaction(BaseModel):
    """One row of the raw ULB creditcard.csv dataset."""

    time: float = Field(..., ge=0, description="Seconds since first transaction")
    v_features: list[float] = Field(..., min_length=28, max_length=28)
    amount: float = Field(..., ge=0)
    label: int = Field(..., description="0 = legitimate, 1 = fraud")

    @field_validator("label")
    @classmethod
    def label_must_be_binary(cls, value: int) -> int:
        if value not in (0, 1):
            raise ValueError(f"label must be 0 or 1, got {value}")
        return value

    @classmethod
    def from_csv_row(cls, row: dict) -> "RawTransaction":
        """Build a RawTransaction from a raw CSV row (V1..V28, Time, Amount, Class)."""
        v_features = [float(row[f"V{i}"]) for i in range(1, 29)]
        return cls(
            time=float(row["Time"]),
            v_features=v_features,
            amount=float(row["Amount"]),
            label=int(row["Class"]),
        )