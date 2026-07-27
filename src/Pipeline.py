"""Phase 1 vertical slice: CSV -> validated rows -> augmented -> features -> feature store.

Usage:
    python -m src.pipeline --input data/raw/creditcard_sample.csv --feature-group transactions_v1
"""

import argparse
import logging

from feature_store.store import FeatureStore
from src.feature_engineering.transform import transform_batch
from src.ingestion.augment import augment_transactions
from src.ingestion.loader import load_transactions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(csv_path: str, feature_group: str) -> str:
    result = load_transactions(csv_path)
    if not result.valid_rows:
        raise RuntimeError("No valid rows ingested; aborting pipeline run.")

    augmented = augment_transactions(result.valid_rows)
    feature_rows = transform_batch(augmented)

    store = FeatureStore()
    version = store.write_feature_group(feature_group, feature_rows)

    logger.info(
        "Pipeline complete: %d rows -> feature group '%s' version %s",
        len(feature_rows),
        feature_group,
        version,
    )
    return version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--feature-group", default="transactions_v1")
    args = parser.parse_args()
    run_pipeline(args.input, args.feature_group)


if __name__ == "__main__":
    main()