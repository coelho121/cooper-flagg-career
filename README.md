# Career Projection

**Can a model project an NBA player's whole career after his rookie season, and say *how* he plays, not just how good he'll be?**

Work in progress. The showcase player is **Cooper Flagg** (#1 pick, 2025), but the
model is built and validated on hundreds of careers; Flagg is the case study.

---

## The idea

Most player projections stop at one number ("he'll be a 20-point scorer"). This
project goes further on two fronts:

1. **Trajectory:** a year-by-year projection of the whole career (value, minutes,
   availability) with honest uncertainty that widens over time, plus milestone
   probabilities (All-Star, All-NBA, MVP-level seasons, Hall of Fame-type career).
2. **Style:** a rich description of the player that goes beyond the box score:
   athleticism, shot diet, how he creates, how he defends. It answers "who does he
   play like" and powers the comparables behind the projection.

## Two layers, and why

The richest style data is recent, but finished careers are old. These two facts
shape the whole design:

| Layer | Purpose | Data | Players |
|---|---|---|---|
| **Trajectory** | predict the career | season stats, age, draft, physicals | careers from ~1980 on (finished ones to learn from) |
| **Style** | describe the player, find look-alikes | combine, shot charts, play types, tracking | ~2013 on, where the data exists |

The trajectory model can't rely on tracking data that almost no finished career has.
The style layer describes and explains; it only feeds the projection where it can be
validated.

## Data plan (draft)

| What | Source | Since |
|---|---|---|
| Season stats, advanced (BPM, VORP, WS), awards | Basketball-Reference via the Kaggle mirror | full history |
| Draft history, game logs | `nba_api` | 1996-97 |
| Athleticism: vertical, lane agility, sprint, wingspan, standing reach, hand size | NBA Draft Combine (`nba_api`) | 2000 |
| Shot diet: every shot's action type (dunk, layup, floater, hook, pull-up, step-back) and zone | Shot charts (`nba_api` `ShotChartDetail`) | 1996-97 |
| Self-created vs assisted shots | play-by-play (`nba_api`) | 1996-97 |
| Play types: isolation, P&R ball handler/roll man, spot-up, transition, post-up, cuts (frequency + efficiency) | Synergy via `nba_api` | 2015-16 |
| Drives, touches, time of possession, catch-and-shoot vs pull-up | Player tracking (`nba_api`) | 2013-14 |
| Defense: matchups (who he guarded), contests, deflections, rim protection | Tracking, hustle and matchup endpoints | 2013-14 to 2017-18 |

## Ideas to explore

- **Archetypes:** cluster players by style (shot diet + play types + physicals) and
  map them in 2D; show Flagg's position moving season by season.
- **Athleticism without the combine:** many top picks skip the athletic tests, so
  build in-game proxies (dunks and rim attempts per 36, transition frequency,
  offensive rebounds, blocks, free-throw rate) and check them against combine
  results where both exist.
- **Development signals:** classic early predictors of improvement, such as
  free-throw % as a predictor of future 3-point shooting, or age-adjusted growth
  between years 1 and 2.
- **Aging curves** that correct for survivorship (players who decline leave the data).
- **Similarity scores** (CARMELO-style): find players most like Flagg at the same age,
  then follow what they became.
- **Career simulation:** Monte Carlo careers (improvement, injuries, decline,
  attrition) to get probabilities instead of one line.
- **Backtests on famous players:** what the model would have said about LeBron,
  Wiggins, Zion, Luka, Edwards after their rookie season.

## Rules of the game

- **No leakage:** every projection uses only data available at its as-of date, and
  backtests replay that exactly.
- **Validated on others, applied to Flagg:** the model is judged on past players;
  a single player can't validate anything.
- **Dated forecast:** the Flagg projection is frozen with its date, to be revisited.

## Builds on

[rookie-projection](https://github.com/) (previous project): what a rookie's first
25 games say about years 3-4 beyond draft position.
