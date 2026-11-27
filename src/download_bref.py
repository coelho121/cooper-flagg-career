""" DDownload the Basketball-Reference Kaggle mirror into data/raw/bref/.

basketball-reference.com blocks scrapers (Cloudflare), so we use the CC0 Kaggle
dataset "NBA Stats (1947-present)" by Sumitro Datta
(`sumitrodatta/nba-aba-baa-stats`), scraped from Basketball-Reference and updated
every season. Player ids are Basketball-Reference slugs (e.g. 'jamesle01').

Downloads work without authentication, but Kaggle answers 404 to the default
`python-requests` User-Agent, so we send a generic one. Files are downloaded one
by one (the list comes from the public listing endpoint), so a single file can be
refreshed without re-downloading everything.

Each file is cached: if it already exists, it is not downloaded again. The
dataset changes as seasons are added, so the cache freezes the version used
here. Delete a file to refresh it.

Run from the project root:
    python src/download_bref.py
"""

import time
from pathlib import Path
from urllib.parse import quote

import requests

DATASET = "sumitrodatta/nba-aba-baa-stats"
LIST_URL = f"https://www.kaggle.com/api/v1/datasets/list/{DATASET}"
FILE_URL = f"https://www.kaggle.com/api/v1/datasets/download/{DATASET}/{{file}}"

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "bref"

TIMEOUT_S = 120
MAX_TRIES = 4
PAUSE_S = 1  # be polite between requests
HEADERS = {"User-Agent": "career-projection/0.1"}  # default UA gets a 404


def get(url: str) -> requests.Response:
    """GET with retries and exponential backoff (5s, 10s, 20s)."""
    for attempt in range(1, MAX_TRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_S)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            if attempt == MAX_TRIES:
                raise
            wait = 5 * 2 ** (attempt - 1)
            print(f"  attempt {attempt} failed ({exc!r}); retrying in {wait}s")
            time.sleep(wait)


def list_files() -> list[str]:
    """Names of all files in the dataset."""
    data = get(LIST_URL).json()
    return sorted(f["nameNullable"] for f in data["datasetFiles"])


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    files = list_files()
    print(f"{len(files)} files in {DATASET}")

    for file in files:
        path = RAW_DIR / file
        if path.exists():
            print(f"  {file}: cached")
            continue
        content = get(FILE_URL.format(file=quote(file))).content
        path.write_bytes(content)
        print(f"  {file}: downloaded ({len(content) / 1e6:.1f} MB)")
        time.sleep(PAUSE_S)


if __name__ == "__main__":
    main()
