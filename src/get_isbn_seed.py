"""
Build a seed list of 1000 random ISBN-13 values using Open Library.

Output:
  data/raw/isbn_seed_1000.csv
"""

from __future__ import annotations

import os
import random
import re
import time
from typing import Iterable, List, Optional, Set

import pandas as pd
import requests

SUBJECT_URL = "https://openlibrary.org/subjects/{slug}.json"
SEARCH_URL = "https://openlibrary.org/search.json"


def safe_get_json(
    url: str,
    params: dict,
    timeout: int = 20,
    retries: int = 3
) -> Optional[dict]:
    """GET JSON with simple retries and a polite user-agent."""
    headers = {"User-Agent": "DSCI510-BookPriceProject/1.0 (educational use)"}

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException as e:
            print(f"[WARN] Request failed (attempt {attempt}/{retries}): {e}")

        time.sleep(0.75 * attempt)

    return None


def normalize_isbn13(values: Iterable[str]) -> Set[str]:
    """Return only clean ISBN-13 digit strings."""
    out: Set[str] = set()
    for v in values:
        if not isinstance(v, str):
            continue
        v = v.strip()
        if len(v) == 13 and v.isdigit():
            out.add(v)
    return out


def subject_slug_variants(subject: str) -> List[str]:
    """
    Create multiple possible Open Library subject slugs from a human subject string.
    Example: "Mystery and Detective Stories" ->
      ["mystery_and_detective_stories", "mystery-and-detective-stories", ...]
    """
    s = subject.strip().lower()

    s = s.replace("&", "and")
    s = re.sub(r"[^\w\s-]", "", s)
    s_space = re.sub(r"\s+", " ", s).strip()

    underscore = s_space.replace(" ", "_")
    hyphen = s_space.replace(" ", "-")
    compact = s_space.replace(" ", "")

    no_and_underscore = underscore.replace("_and_", "_")
    no_and_hyphen = hyphen.replace("-and-", "-")

    variants: List[str] = []
    for v in [underscore, hyphen, no_and_underscore, no_and_hyphen, compact]:
        if v and v not in variants:
            variants.append(v)

    return variants


def fetch_isbns_via_subject_endpoint(
    slug: str,
    max_pages: int = 12,
    sleep_s: float = 0.35
) -> Set[str]:
    """Collect ISBN-13s from the /subjects/{slug}.json endpoint."""
    isbns: Set[str] = set()
    url = SUBJECT_URL.format(slug=slug)

    for page in range(max_pages):
        params = {"limit": 50, "offset": page * 50}
        data = safe_get_json(url, params=params)
        if not data:
            break

        works = data.get("works", [])
        if not works:
            break

        for work in works:
            if "isbn_13" in work and isinstance(work["isbn_13"], list):
                isbns |= normalize_isbn13(work["isbn_13"])
            if "isbn" in work and isinstance(work["isbn"], list):
                isbns |= normalize_isbn13(work["isbn"])

            editions = work.get("editions", [])
            for ed in editions:
                if "isbn_13" in ed and isinstance(ed["isbn_13"], list):
                    isbns |= normalize_isbn13(ed["isbn_13"])
                if "isbn" in ed and isinstance(ed["isbn"], list):
                    isbns |= normalize_isbn13(ed["isbn"])

        time.sleep(sleep_s)

    return isbns


def fetch_isbns_via_search_endpoint(
    subject_query: str,
    max_pages: int = 40,
    sleep_s: float = 0.25
) -> Set[str]:
    """
    Collect ISBN-13s using /search.json?subject=<subject>.
    """
    isbns: Set[str] = set()

    for page in range(1, max_pages + 1):
        params = {
            "subject": subject_query,
            "limit": 100,
            "page": page,
            "fields": "isbn,title,author_name,key",
        }
        data = safe_get_json(SEARCH_URL, params=params)
        if not data:
            break

        docs = data.get("docs", [])
        if not docs:
            break

        for d in docs:
            isbn_list = d.get("isbn", [])
            if isinstance(isbn_list, list):
                isbns |= normalize_isbn13(isbn_list)

        time.sleep(sleep_s)

    return isbns


def fetch_isbns_for_subject(subject: str) -> Set[str]:
    """
    Robust subject ISBN collection:
    1) Try multiple subject slugs on /subjects/{slug}.json
    2) Fallback to /search.json?subject=<subject> if needed
    """
    collected: Set[str] = set()

    variants = subject_slug_variants(subject)
    best_slug = None
    best_count = 0

    for slug in variants:
        isbns = fetch_isbns_via_subject_endpoint(slug)
        if len(isbns) > best_count:
            best_count = len(isbns)
            best_slug = slug
            collected = isbns

        if best_count >= 250:
            break

    if best_slug and best_count > 0:
        print(f"[INFO]   subject endpoint worked: slug='{best_slug}' -> {best_count} ISBN-13s")
        return collected

    isbns_search = fetch_isbns_via_search_endpoint(subject)
    print(f"[INFO]   fallback search endpoint: subject='{subject}' -> {len(isbns_search)} ISBN-13s")
    return isbns_search


def collect_isbns(subjects: Iterable[str]) -> Set[str]:
    """Collect ISBN-13s across multiple human-readable subjects."""
    all_isbns: Set[str] = set()

    for subject in subjects:
        print(f"[INFO] Fetching ISBNs for: {subject}")
        isbns = fetch_isbns_for_subject(subject)
        print(f"[INFO]   total captured for '{subject}': {len(isbns)}")
        all_isbns.update(isbns)

    return all_isbns


def sample_isbns(isbns: Set[str], n: int = 1000, seed: int = 42) -> List[str]:
    """Random sample with reproducibility."""
    isbns_list = sorted(isbns)
    if len(isbns_list) < n:
        raise ValueError(f"Not enough ISBN-13s collected to sample {n}. Collected={len(isbns_list)}")
    random.seed(seed)
    return random.sample(isbns_list, n)


def save_isbns_to_csv(isbns: List[str], filepath: str) -> None:
    """Save ISBNs to CSV at the given path."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pd.DataFrame({"isbn": isbns}).to_csv(filepath, index=False)


def main() -> None:
    subjects = [
        "Art",
        "Science Fiction",
        "Fantasy",
        "Biographies",
        "Children",
        "Recipes",
        "Romance",
        "History",
        "Mystery and Detective Stories",
        "Medicine",
        "Religion",
        "Plays",
        "Science",
    ]

    print("[INFO] Collecting ISBNs from Open Library (robust mode)...")
    all_isbns = collect_isbns(subjects)
    print(f"[INFO] Total unique ISBN-13 collected: {len(all_isbns)}")

    sampled = sample_isbns(all_isbns, n=1000, seed=42)
    output_path = "data/raw/isbn_seed_1000.csv"
    save_isbns_to_csv(sampled, output_path)

    print(f"[DONE] Saved {len(sampled)} ISBNs to: {output_path}")


if __name__ == "__main__":
    main()
