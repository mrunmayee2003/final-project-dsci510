"""""
Input:
  data/raw/isbn_seed_1000.csv   (column: isbn)

Outputs:
  data/raw/abebooks_raw.csv     (all listings in a single CSV)
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

ABEBOKS_SEARCH_URL = "https://www.abebooks.com/servlet/SearchResults"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_get(
    url: str,
    params: dict,
    timeout: int = 25,
    retries: int = 3,
    sleep_backoff: float = 1.0,
) -> Optional[str]:
    """GET HTML with retries and simple backoff. Returns HTML text or None."""
    headers = {
        "User-Agent": "DSCI510-BookPriceProject/1.0 (educational use)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200 and r.text:
                return r.text
            print(f"[WARN] HTTP {r.status_code} for params={params}")
        except requests.RequestException as e:
            print(f"[WARN] Request error attempt {attempt}/{retries}: {e}")

        time.sleep(sleep_backoff * attempt)

    return None


def parse_price(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse something like '$12.34' or 'US$ 12.34' into (12.34, 'USD').
    """
    if not text:
        return None, None

    t = text.strip()

    currency = None
    if "US$" in t or "$" in t:
        currency = "USD"
    elif "£" in t:
        currency = "GBP"
    elif "€" in t:
        currency = "EUR"

    m = re.search(r"(\d+(?:\.\d{1,2})?)", t.replace(",", ""))
    if not m:
        return None, currency

    try:
        return float(m.group(1)), currency
    except ValueError:
        return None, currency


def normalize_condition(text: Optional[str]) -> Optional[str]:
    """Standardize condition labels into a few buckets."""
    if not text:
        return None
    t = text.strip().lower()

    if "like new" in t:
        return "like_new"
    if "very good" in t:
        return "used_very_good"
    if "good" in t:
        return "used_good"
    if "acceptable" in t:
        return "used_acceptable"
    if "new" in t:
        return "new"
    if "used" in t:
        return "used"

    return t.replace(" ", "_")


@dataclass
class Listing:
    source: str
    isbn: str
    title: Optional[str]
    author: Optional[str]
    listing_price: Optional[float]
    shipping_price: Optional[float]
    total_price: Optional[float]
    currency: Optional[str]
    condition: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    url: Optional[str]
    scrape_time_utc: str


def parse_abebooks_search(html: str, isbn: str) -> List[Listing]:
    """
    Parse AbeBooks SearchResults page for a given ISBN.
    """
    soup = BeautifulSoup(html, "lxml")
    scrape_time = utc_now_iso()
    listings: List[Listing] = []

    result_cards = soup.select("[data-cy='listing-item']")
    if not result_cards:
        result_cards = soup.select(".result, .result-item, .cf.result, .srp-item")

    if not result_cards:
        return listings

    for card in result_cards[:25]:
        title = None
        url = None

        a = card.select_one("a")
        if a and a.get_text(strip=True):
            title = a.get_text(strip=True)
            href = a.get("href")
            if href:
                url = href if href.startswith("http") else f"https://www.abebooks.com{href}"

        author = None
        author_el = card.select_one("[data-cy='author'], .author, .author-name")
        if author_el:
            author = author_el.get_text(" ", strip=True)

        condition = None
        cond_el = card.select_one("[data-cy='condition'], .condition, .item-condition")
        if cond_el:
            condition = normalize_condition(cond_el.get_text(" ", strip=True))

        listing_price = None
        currency = None
        price_el = card.select_one("[data-cy='price'], .price, .item-price")
        if price_el:
            listing_price, currency = parse_price(price_el.get_text(" ", strip=True))

        shipping_price = None
        ship_el = card.select_one("[data-cy='shipping'], .shipping, .item-shipping")
        if ship_el:
            shipping_price, ship_currency = parse_price(ship_el.get_text(" ", strip=True))
            if not currency and ship_currency:
                currency = ship_currency

        total_price = None
        if listing_price is not None and shipping_price is not None:
            total_price = listing_price + shipping_price
        elif listing_price is not None:
            total_price = listing_price

        listings.append(
            Listing(
                source="abebooks",
                isbn=isbn,
                title=title,
                author=author,
                listing_price=listing_price,
                shipping_price=shipping_price,
                total_price=total_price,
                currency=currency,
                condition=condition,
                rating=None,
                review_count=None,
                url=url,
                scrape_time_utc=scrape_time,
            )
        )

    return listings


def scrape_abebooks_for_isbn(isbn: str) -> List[Listing]:
    params = {"isbn": isbn}
    html = safe_get(ABEBOKS_SEARCH_URL, params=params)
    if not html:
        return []

    html_dir = Path("data/raw/abebooks_html")
    html_dir.mkdir(parents=True, exist_ok=True)
    (html_dir / f"{isbn}.html").write_text(html, encoding="utf-8")

    return parse_abebooks_search(html, isbn)


def main() -> None:
    isbn_path = "data/raw/isbn_seed_1000.csv"
    out_jsonl = "data/raw/abebooks_raw.jsonl"
    out_csv = "data/raw/abebooks_raw.csv"

    df = pd.read_csv(isbn_path)
    isbns = df["isbn"].astype(str).dropna().unique().tolist()

    all_rows: List[Dict] = []
    Path("data/raw").mkdir(parents=True, exist_ok=True)

    with open(out_jsonl, "w", encoding="utf-8") as f_jsonl:
        for i, isbn in enumerate(isbns, start=1):
            print(f"[INFO] ({i}/{len(isbns)}) Scraping AbeBooks for ISBN: {isbn}")
            listings = scrape_abebooks_for_isbn(isbn)

            for listing in listings:
                row = asdict(listing)
                f_jsonl.write(json.dumps(row, ensure_ascii=False) + "\n")
                all_rows.append(row)

            time.sleep(1.0)

    if all_rows:
        pd.DataFrame(all_rows).to_csv(out_csv, index=False)
        print(f"[DONE] Saved {len(all_rows)} listings to:\n  {out_jsonl}\n  {out_csv}")
    else:
        print("[DONE] No listings captured.")


if __name__ == "__main__":
    main()
