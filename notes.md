# Notes

## Flow

### 2026-11-21
- Project setup: `.venv` (Python 3.12), folders `data/raw`, `data/processed`, `src/`, `notebooks/`, `requirements.txt`.

### 2026-11-23
- `src/download_bref.py`: downloads all 20 files of the Kaggle Basketball-Reference mirror to `data/raw/bref/`, file by file, with caching, retries and backoff.
- Validated against known values: LeBron 2008-09 BPM 13.2, VORP 11.8 (exact match, same check as rookie-projection).

## Decisions

### 2026-11-21
- Python 3.12 for the venv, not 3.14: numpy is pinned at 2.2.6 (Smart App Control issue in rookie-projection) and 2.2.6 has no wheels for 3.14.
- `data/` added to `.gitignore`; all data must be regenerable from `src/` scripts.
- Base packages: numpy, pandas, matplotlib, seaborn, scikit-learn, scipy, requests, nba_api, ipykernel. Versions unpinned except numpy; pin once the environment is stable.

### 2026-11-23
- Download all 20 mirror files, not just stats and advanced: awards (All-Star, All-NBA, MVP voting) are needed for the milestone probabilities, and `Player Shooting.csv` and `Player Play By Play.csv` (from 1997) give early style data (shot distance, % assisted, dunks, positions).
- Download file by file, not the whole zip, so a single file can be refreshed.
- The cache freezes the mirror at its download date (2026-11-23). The 2026-27 season is in progress (5-7 games per player) and is frozen at that point.

## Problems

### 2026-11-23
- Kaggle answers **404** (not 403) to the default `python-requests` User-Agent, while `curl` works. That looked like a wrong URL. Fixed by sending a generic User-Agent. rookie-projection's script did not need this, so Kaggle changed something since then.

## Findings

### 2026-11-23
- Data convention: `season` is the year the season ends (2026 = 2025-26).
- Mirror covers 1947 to 2027 (current season, partial). Shooting and play-by-play tables start in 1997.
- Flagg 2025-26 (rookie, age 19): 70 games, 2344 min, 1473 pts (21.0 ppg), BPM 1.4, VORP 2.0, WS 3.8. 2026-27 so far: 5 games, BPM 11.0 (tiny sample).
