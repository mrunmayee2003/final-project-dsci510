"""
Clean raw AbeBooks and BookFinder(Amazon) data into processed CSVs.

Inputs:
  data/raw/abebooks_raw.csv
  data/raw/bookfinder_amzn_raw.csv

Outputs:
  data/processed/abebooks_cleaned.csv
  data/processed/amazon_cleaned.csv
"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd


ABEBEOKS_INPUT = "data/raw/abebooks_raw.csv"
ABEBOOKS_OUTPUT = "data/processed/abebooks_cleaned.csv"

BOOKFINDER_INPUT = "data/raw/bookfinder_amzn_raw.csv"
AMAZON_OUTPUT = "data/processed/amazon_cleaned.csv"


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def clean_abebooks() -> pd.DataFrame:
    print("=== Cleaning AbeBooks data ===")
    df = pd.read_csv(ABEBEOKS_INPUT)
    print(f"Original AbeBooks shape: {df.shape}")

    columns_to_keep = ["source", "isbn", "author", "total_price", "currency"]
    df_filtered = df[columns_to_keep].copy()
    print(f"After selecting columns: {df_filtered.shape}")

    # Prefer lowest price per ISBN (usually more meaningful)
    df_sorted = df_filtered.sort_values("total_price", ascending=True)
    df_cleaned = df_sorted.drop_duplicates(subset=["isbn"], keep="first")

    print(f"After dedupe by ISBN: {df_cleaned.shape}")
    df_final = df_cleaned[["isbn", "source", "author", "total_price", "currency"]]

    ensure_dir(ABEBOOKS_OUTPUT)
    df_final.to_csv(ABEBOOKS_OUTPUT, index=False)
    print(f"✔ AbeBooks cleaned saved to {ABEBOOKS_OUTPUT}")
    return df_final


def is_valid_price(price: Any) -> bool:
    """Check if price is valid (numeric, > 0, not 13-digit ISBN-like)."""
    price_str = str(price).strip()

    if price_str in ("", "nan"):
        return False

    try:
        price_float = float(price_str)
    except (ValueError, TypeError):
        return False

    if 1000000000000 <= price_float <= 9999999999999:
        return False
    if price_float <= 0:
        return False

    return True


def clean_bookfinder_amazon() -> pd.DataFrame:
    print("=== Cleaning BookFinder(Amazon.com) data ===")
    df = pd.read_csv(BOOKFINDER_INPUT)
    print(f"Original BookFinder shape: {df.shape}")

    df_filtered = df[df["raw_website_name"].str.contains("Amazon.com", case=False, na=False)].copy()
    print(f"After filtering for Amazon.com: {df_filtered.shape}")

    df_cleaned = df_filtered[["isbn", "raw_website_name", "book_title", "price"]].copy()
    df_cleaned.columns = ["isbn", "source", "book_title", "price"]
    print(f"After selecting columns: {df_cleaned.shape}")

    before = df_cleaned.shape[0]
    df_cleaned = df_cleaned[df_cleaned["price"].apply(is_valid_price)].copy()
    print(f"After removing invalid prices: {df_cleaned.shape} (removed {before - df_cleaned.shape[0]})")

    df_cleaned["price"] = pd.to_numeric(df_cleaned["price"], errors="coerce")

    before_dedup = df_cleaned.shape[0]
    df_cleaned = (
        df_cleaned.sort_values("price", ascending=True)
        .drop_duplicates(subset=["isbn"], keep="first")
        .sort_values("isbn")
        .reset_index(drop=True)
    )
    print(f"After dedupe by ISBN: {df_cleaned.shape} (removed {before_dedup - df_cleaned.shape[0]})")

    ensure_dir(AMAZON_OUTPUT)
    df_cleaned.to_csv(AMAZON_OUTPUT, index=False)
    print(f"✔ Amazon cleaned saved to {AMAZON_OUTPUT}")
    return df_cleaned


def main() -> None:
    clean_abebooks()
    clean_bookfinder_amazon()
    print("All cleaning steps complete.")


if __name__ == "__main__":
    main()
