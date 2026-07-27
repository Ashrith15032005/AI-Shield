"""CLI helper to create a small, stratified sample of the raw dataset.

Keeps the fraud/legitimate ratio roughly intact so the sample stays
representative of the ~0.17% fraud class imbalance, even at small n.
Usage:
    python -m src.ingestion.sample --input data/raw/creditcard.csv \\
        --output data/raw/creditcard_sample.csv --n 20000
"""

import argparse

import pandas as pd


def stratified_sample(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    fraud_frac = df["Class"].mean()
    n_fraud = max(1, round(n * fraud_frac))
    n_legit = n - n_fraud

    fraud_rows = df[df["Class"] == 1].sample(
        n=min(n_fraud, (df["Class"] == 1).sum()), random_state=seed
    )
    legit_rows = df[df["Class"] == 0].sample(
        n=min(n_legit, (df["Class"] == 0).sum()), random_state=seed
    )
    return pd.concat([fraud_rows, legit_rows]).sample(frac=1, random_state=seed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--n", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    sampled = stratified_sample(df, n=args.n, seed=args.seed)
    sampled.to_csv(args.output, index=False)
    print(f"Wrote {len(sampled)} rows ({sampled['Class'].mean():.4%} fraud) to {args.output}")


if __name__ == "__main__":
    main()