# Notes

## Flow

### 2026-11-21
- Project setup: `.venv` (Python 3.12), folders `data/raw`, `data/processed`, `src/`, `notebooks/`, `requirements.txt`.

### 2026-11-23
- `src/download_bref.py`: downloads all 20 files of the Kaggle Basketball-Reference mirror to `data/raw/bref/`, file by file, with caching, retries and backoff.
- Validated against known values: LeBron 2008-09 BPM 13.2, VORP 11.8 (exact match, same check as rookie-projection).
- `src/build_seasons.py` → `data/processed/player_seasons.parquet`: 27,452 player-seasons × 117 columns (totals, advanced, shooting, play-by-play, experience, awards, draft, career info). Checks: row count equals unique player-seasons in the raw totals; exactly 1 MVP per season; 5 first-team All-NBA per season since 1990; Harden 2020-21 is one row (HOU/BRK).
- Added Flagg's 2025-26 awards by hand (ROY share 0.824, All-Rookie 1st team) and `main.py`, which runs the pipeline end to end.

## Decisions

### 2026-11-21
- Python 3.12 for the venv, not 3.14: numpy is pinned at 2.2.6 (Smart App Control issue in rookie-projection) and 2.2.6 has no wheels for 3.14.
- `data/` added to `.gitignore`; all data must be regenerable from `src/` scripts.
- Base packages: numpy, pandas, matplotlib, seaborn, scikit-learn, scipy, requests, nba_api, ipykernel. Versions unpinned except numpy; pin once the environment is stable.

### 2026-11-23
- Download all 20 mirror files, not just stats and advanced: awards (All-Star, All-NBA, MVP voting) are needed for the milestone probabilities, and `Player Shooting.csv` and `Player Play By Play.csv` (from 1997) give early style data (shot distance, % assisted, dunks, positions).
- Download file by file, not the whole zip, so a single file can be refreshed.
- The cache freezes the mirror at its download date (2026-11-23). The 2026-27 season is in progress (5-7 games per player) and is frozen at that point.
- **As-of point: after the rookie season**, not after a season and a half (README and CLAUDE.md updated). We project now with the data that exists rather than waiting until February. Backtests must use the same information set: the full rookie season. The mirror has only season totals, so "rookie season + N games" can't be replayed for past players without game logs. Flagg's first 2026-27 games are shown descriptively only, not fed to the model.
- Multi-team seasons: keep the combined '2TM'/'3TM' row (so each player-season counts once), store the teams in `teams` and `n_teams`.
- Keep all leagues (NBA, ABA, BAA) with an `lg` column. Dropping ABA would make ABA-to-NBA players like Erving look like 26-year-old rookies. `experience` (from the mirror) already counts ABA seasons.
- Players drafted more than once (158, older eras) keep their latest selection.
- Processed data saved as parquet (keeps dtypes: dates, booleans, nullable ints). Added `pyarrow`.
- `in_progress` flag on season 2027: never a training target.
- **ROY as a candidate feature.** It is announced at the end of the rookie season, so it is known at the as-of date (no leakage). Use the vote share (`roy_share`), not just the winner: one winner a year (~45 since 1980) is too sparse, while shares cover the top 5-10 rookies. Whether it adds information beyond the rookie stats (it mostly reflects them) gets tested in the backtests with and without it.
- **Manual award patches** (`MANUAL_AWARDS` in `build_seasons.py`): the mirror lacks the 2025-26 awards. Flagg's ROY (56 first-place + 44 second-place votes = 412 of 500 points, 5-3-1 scoring → share 0.824) and All-Rookie 1st team were entered by hand from the NBA's official release and Bleacher Report. A patch never overwrites the mirror and is skipped once the mirror has the award. Only Flagg is patched: other 2025-26 rookies have no finished careers, so they don't enter training.
- **Pipeline instead of notebooks for logic.** All logic in `src/` modules with a `main()`, `main.py` runs everything end to end, notebooks only explore and present (importing from `src/`). Reason: notebooks have hidden state (cells run out of order), give noisy Git diffs and can't be run as one reproducible command. With "clone the repo, run `python main.py`, get every result", anyone can check the work. CLAUDE.md updated.

## Problems

### 2026-11-23
- Kaggle answers **404** (not 403) to the default `python-requests` User-Agent, while `curl` works. That looked like a wrong URL. Fixed by sending a generic User-Agent. rookie-projection's script did not need this, so Kaggle changed something since then.
- Award vote shares and End of Season Teams (All-NBA, All-Defense, All-Rookie) stop at 2024-25; only All-Star selections include 2025-26. Flagg's rookie awards (ROY vote, All-Rookie) are missing. Not a problem for training (finished careers are complete), but revisit when the mirror updates.
- Minor gaps: 12 players without birth date, 4 seasons since 1974 without BPM, 71 seasons since 1997 without shooting splits (probably players with almost no shots). Check before modelling.

## Findings

### 2026-11-23
- Data convention: `season` is the year the season ends (2026 = 2025-26).
- Mirror covers 1947 to 2027 (current season, partial). Shooting and play-by-play tables start in 1997.
- Flagg 2025-26 (rookie, age 19): 70 games, 2344 min, 1473 pts (21.0 ppg), BPM 1.4, VORP 2.0, WS 3.8. 2026-27 so far: 5 games, BPM 11.0 (tiny sample).
