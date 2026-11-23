"""Run the whole pipeline end to end.

    python main.py

Each step caches its output, so re-running is cheap: downloads are skipped when
the raw files exist, and processing steps rebuild from data/raw/.
New steps (features, model, backtests, simulation, figures) get added here as
they are built.
"""

from src import build_seasons, download_bref

STEPS = [
    ("Download Basketball-Reference mirror", download_bref.main),
    ("Build player-season table", build_seasons.main),
]


def main() -> None:
    for i, (name, step) in enumerate(STEPS, start=1):
        print(f"\n[{i}/{len(STEPS)}] {name}")
        step()
    print("\nPipeline finished.")


if __name__ == "__main__":
    main()
