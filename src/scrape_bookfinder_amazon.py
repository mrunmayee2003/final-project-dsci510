"""
Scrape BookFinder ISBN pages and extract offer blocks,
then keep Amazon.com offers.

Input:
  data/raw/isbn_seed_1000.csv

Output:
  data/raw/bookfinder_amzn_raw.csv
"""

from __future__ import annotations

import random
import re
import time
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

INPUT_CSV = "data/raw/isbn_seed_1000.csv"
RAW_OUTPUT = "data/raw/bookfinder_amzn_raw.csv"

MIN_DELAY = 1.2
MAX_DELAY = 2.5
TIMEOUT = 20


def clean(text: str | None) -> str | None:
    return re.sub(r"\s+", " ", text).strip() if text else None


def build_url(isbn: str) -> str:
    return (
        f"https://www.bookfinder.com/isbn/{isbn}/"
        f"?binding=ANY&condition=ANY&currency=USD&destination=US"
    )


def extract_price(text: str | None) -> float | None:
    if not text:
        return None
    m = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", text.replace(",", ""))
    return float(m.group(1)) if m else None


def get_book_title(soup: BeautifulSoup) -> str | None:
    h1 = soup.find("h1")
    return clean(h1.get_text()) if h1 else None


def scrape_isbn(session: requests.Session, isbn: str) -> List[Dict]:
    url = build_url(isbn)
    r = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=TIMEOUT)

    if r.status_code != 200:
        print(f"[WARN] HTTP {r.status_code} for ISBN {isbn}")
        return []

    if re.search(r"given id is invalid|invalid isbn", r.text, re.I):
        return []

    soup = BeautifulSoup(r.text, "lxml")
    title = get_book_title(soup)

    rows: List[Dict] = []

    nodes = soup.find_all(string=re.compile("Edition:", re.I))
    for node in nodes:
        block = node.parent
        for _ in range(6):
            if not block:
                break
            t = block.get_text(" ", strip=True)
            if "Condition:" in t and ("$" in t or "US$" in t):
                break
            block = block.parent

        if not block:
            continue

        text = clean(block.get_text(" ", strip=True))

        website = None
        img = block.find("img")
        if img and img.get("alt"):
            website = clean(img["alt"])

        price = extract_price(text)

        edition = None
        m = re.search(r"Edition:\s*([^|]+)", text)
        if m:
            edition = clean(m.group(1))

        condition = None
        m = re.search(r"Condition:\s*([^|]+)", text)
        if m:
            condition = clean(m.group(1))

        offer_type = "used"
        if condition and "new" in condition.lower():
            offer_type = "new"

        rows.append(
            {
                "isbn": isbn,
                "book_title": title,
                "raw_website_name": website,
                "offer_type": offer_type,
                "price": price,
                "edition": edition,
                "condition": condition,
            }
        )

    return rows


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    isbns = df["isbn"].astype(str).tolist()

    all_rows: List[Dict] = []

    with requests.Session() as session:
        for i, isbn in enumerate(isbns, 1):
            print(f"[{i}/{len(isbns)}] {isbn}")
            try:
                all_rows.extend(scrape_isbn(session, isbn))
            except Exception as e:  # noqa: BLE001
                print("Error:", isbn, e)

            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    out = pd.DataFrame(all_rows)
    out.to_csv(RAW_OUTPUT, index=False)
    print(f"\nSaved raw data → {RAW_OUTPUT}")


if __name__ == "__main__":
    main()
