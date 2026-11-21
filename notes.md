# Notes

## Flow

### 2026-11-21
- Project setup: `.venv` (Python 3.12), folders `data/raw`, `data/processed`, `src/`, `notebooks/`, `requirements.txt`.

## Decisions

### 2026-11-21
- Python 3.12 for the venv, not 3.14: numpy is pinned at 2.2.6 (Smart App Control issue in rookie-projection) and 2.2.6 has no wheels for 3.14.
- `data/` added to `.gitignore`; all data must be regenerable from `src/` scripts.
- Base packages: numpy, pandas, matplotlib, seaborn, scikit-learn, scipy, requests, nba_api, ipykernel. Versions unpinned except numpy; pin once the environment is stable.

## Problems

## Findings
