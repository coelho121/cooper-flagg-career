"""Build one clean player-season table from the Basketball-Reference mirror.

Input:  data/raw/bref/*.csv   (from src/download_bref.py)
Output: data/processed/player_seasons.parquet

One row per (player_id, season, lg). What the script does:

1. Players traded mid-season appear once per team plus a combined row
   ('2TM', '3TM', ...). We keep only the combined row, so every player-season
   counts once, and store the individual teams in `teams` / `n_teams`.
2. Joins season tables: totals, advanced, shooting and play-by-play
   (the last two exist from 1996-97 on; earlier seasons get NaN).
3. Adds career info (birth date, height, weight, Hall of Fame), draft position
   and season awards (All-Star, All-NBA, All-Defense, award vote shares).
4. Flags the season still in progress (`in_progress`), which must never be
   used as a training target.

All leagues (NBA, ABA, BAA) are kept with an `lg` column: dropping ABA
seasons would make ABA-to-NBA players (e.g. Julius Erving) look like
26-year-old rookies. Modelling code decides what to filter.

Run from the project root:
    python src/build_seasons.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "bref"
OUT_PATH = ROOT / "data" / "processed" / "player_seasons.parquet"

CURRENT_SEASON = 2027  # 2026-27, in progress when the mirror was downloaded
KEY = ["player_id", "season", "lg"]
MULTI_TEAM = r"^\dTM$"  # '2TM', '3TM', ...


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / f"{name}.csv")


def one_row_per_season(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the combined row for multi-team seasons, drop the per-team rows."""
    n_rows = df.groupby(KEY)["team"].transform("size")
    is_combined = df["team"].str.match(MULTI_TEAM, na=False)
    out = df[(n_rows == 1) | is_combined]
    assert not out.duplicated(KEY).any(), "player-season still duplicated"
    return out


def team_lists(totals: pd.DataFrame) -> pd.DataFrame:
    """Teams each player played for in a season, in the mirror's order."""
    per_team = totals[~totals["team"].str.match(MULTI_TEAM, na=False)]
    return (
        per_team.groupby(KEY)["team"]
        .agg(teams=lambda t: "/".join(t), n_teams="size")
        .reset_index()
    )


def add_table(base: pd.DataFrame, name: str) -> pd.DataFrame:
    """Left-join a season table, adding only the columns base doesn't have."""
    df = one_row_per_season(read(name))
    new_cols = [c for c in df.columns if c not in base.columns]
    return base.merge(df[KEY + new_cols], on=KEY, how="left", validate="1:1")


def season_awards() -> pd.DataFrame:
    """Per player-season award columns (NBA awards only)."""
    key = ["player_id", "season"]

    allstar = read("All-Star Selections")
    allstar = allstar[allstar["lg"] == "NBA"][key].drop_duplicates()
    allstar["all_star"] = True

    teams = read("End of Season Teams")
    teams["team_num"] = teams["number_tm"].str[0].astype(float)  # '1st' -> 1
    pieces = [allstar]
    for kind, col in [
        ("All-NBA", "all_nba_team"),
        ("All-Defense", "all_defense_team"),
        ("All-Rookie", "all_rookie_team"),
    ]:
        t = teams[(teams["lg"] == "NBA") & (teams["type"] == kind)]
        pieces.append(t.groupby(key)["team_num"].min().rename(col).reset_index())

    shares = read("Player Award Shares")
    for award in ["mvp", "roy", "dpoy", "smoy", "mip"]:
        a = shares[shares["award"] == f"nba {award}"]
        a = a.groupby(key).agg(share=("share", "max"), won=("winner", "max"))
        a.columns = [f"{award}_share", f"{award}_won"]
        pieces.append(a.reset_index())

    out = pieces[0]
    for p in pieces[1:]:
        out = out.merge(p, on=key, how="outer")
    out["lg"] = "NBA"
    return out


def draft_info() -> pd.DataFrame:
    """Draft year and pick. Players drafted twice keep their latest selection."""
    d = read("Draft Pick History").sort_values("season")
    d = d.drop_duplicates("player_id", keep="last")
    return d[["player_id", "season", "overall_pick", "round"]].rename(
        columns={"season": "draft_year", "round": "draft_round"}
    )


def career_info() -> pd.DataFrame:
    c = read("Player Career Info")
    c["birth_date"] = pd.to_datetime(c["birth_date"])
    return c[["player_id", "birth_date", "ht_in_in", "wt", "hof", "from", "to"]].rename(
        columns={"ht_in_in": "height_in", "wt": "weight_lb", "from": "first_season", "to": "last_season"}
    )


def main() -> None:
    totals = read("Player Totals")
    df = one_row_per_season(totals).drop(columns="trp_dbl")
    df = df.merge(team_lists(totals), on=KEY, how="left", validate="1:1")
    df["n_teams"] = df["n_teams"].fillna(1).astype(int)
    df["teams"] = df["teams"].fillna(df["team"])

    for name in ["Advanced", "Player Shooting", "Player Play By Play", "Player Season Info"]:
        df = add_table(df, name)

    awards = season_awards()
    df = df.merge(awards, on=KEY, how="left", validate="1:1")
    for col in ["all_star"] + [c for c in awards if c.endswith("_won")]:
        df[col] = df[col].fillna(False).astype(bool)
    for col in [c for c in awards if c.endswith("_share")]:
        df[col] = df[col].fillna(0.0)

    df = df.copy()  # defragment after the many column-wise merges
    df = df.merge(draft_info(), on="player_id", how="left", validate="m:1")
    df["undrafted"] = df["overall_pick"].isna()
    df = df.merge(career_info(), on="player_id", how="left", validate="m:1")

    df["in_progress"] = df["season"] == CURRENT_SEASON
    df = df.sort_values(["player_id", "season", "lg"]).reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    print(f"Saved {len(df):,} player-seasons x {df.shape[1]} columns to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
