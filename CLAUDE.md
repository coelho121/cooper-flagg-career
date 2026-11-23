# CLAUDE.md — Career Projection

## About me
- Martim Coelho, 3rd-year Information Management student at NOVA IMS (Lisbon). Portfolio project for a career in sports analytics.
- Still getting used to the tooling (Git, VS Code, venvs, scraping). Explain the *why* behind each step at a level I could defend in a job interview. Don't just dump code.
- Talk to me in Portuguese (PT-PT), casual tone. Code, comments, notes and the README are in English.
- Windows. Virtual environment `.venv` (activate with `.venv\Scripts\activate`).
- **Every project ends in a YouTube video.** Keep that in mind when choosing analyses and figures: strong hooks, visuals that read on screen, stories about real players. Never at the cost of honesty.

## The project
**Question:** after his rookie season, can we project Cooper Flagg's whole NBA career, year by year, and describe *how* he plays?

Read `README.md` (idea, two-layer design, data plan) and `notes.md` (decisions and history) at the start of every session.

### Ambition: go deep
I want this to be rich and interesting, not "standard per-season stats and done". Push for depth:
- Style beyond the box score: athleticism (combine + in-game proxies), shot diet (dunk vs layup vs floater vs mid-range vs pull-up 3, assisted vs self-created), play types, tracking (drives, touches, catch-and-shoot), defensive matchups.
- Proper methods: similarity scores, survivorship-corrected aging curves, archetype clustering, Monte Carlo career simulation, milestone probabilities.
- Proactively suggest richer data or angles when you see them, but say what each one costs (requests, missing years, complexity) and whether it can be validated.

### Design rules
- **Two layers:** trajectory (long history, finished careers) and style (recent, rich data). Don't train the career model on data that finished careers don't have; the style layer describes and finds comparables.
- **No leakage:** every projection, including backtests, uses only data available at its as-of date.
- **Validate on others, apply to Flagg.** Backtest on past players (famous ones make the best video moments).
- **No survivorship bias:** players who left the league or declined stay in the data.
- Freeze the Flagg forecast with its date.

## Data notes (lessons from rookie-projection)
- basketball-reference.com blocks scrapers (403 / Cloudflare). Use the Kaggle mirror (`sumitrodatta/nba-aba-baa-stats`, CC0), downloadable without auth from `https://www.kaggle.com/api/v1/datasets/download/...`, and validate it against known values.
- `nba_api` can be slow or time out: timeouts, retries with backoff, a pause between requests. Shot charts and tracking are one request per player-season: plan request counts and cache everything.
- Many top picks skip the combine's athletic tests: check coverage before relying on it.
- Windows Smart App Control blocked numpy 2.5.x DLLs: numpy is pinned at 2.2.6. If a DLL import fails once, retry before debugging (it was transient for sklearn).
- Always cache raw downloads in `data/raw/` and never re-download what's there. Cleaned data in `data/processed/`.

## Repo rules
- `data/` is gitignored. Never commit data; scripts in `src/` must regenerate it.
- Reusable data and cleaning code in `src/` (scripts); exploration and modelling in `notebooks/`.
- When installing a package, add it to `requirements.txt`.
- **I do commits and pushes myself in GitHub Desktop.** Don't run `git commit` or `git push`. When a step is done, suggest a short commit message.
- Before rewriting a notebook, warn me to close it in VS Code (or "Revert File" afterwards), or VS Code shows a stale version.

## Notes and README
- `notes.md` has four sections: **Flow, Decisions, Problems, Findings**. Each main topic gets a date heading (`### YYYY-MM-DD`); subtopics don't.
- Write notes updates directly, without waiting for my confirmation.
- The README currently holds the plan. At the end it gets rewritten from the notes to present the results.
