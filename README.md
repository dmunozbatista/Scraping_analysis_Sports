# Football Data Web

Scrape, clean, and visualize football player statistics from [fbref.com](https://fbref.com) for any selected player across major European leagues.

## Objective

Given a player name and a league, the app automatically:

1. Scrapes all player stats from fbref.com for that league
2. Cleans and transforms the raw data (type casting, derived metrics, per-90 normalization)
3. Generates visualizations that place the selected player in context among the top forwards in the league

The default example is **Lamine Yamal** in La Liga.

## Data Source

All data is scraped from **[fbref.com](https://fbref.com)** (Football Reference), which provides detailed football statistics including expected goals (xG), expected assists (xA), progressive carries, and more. Please respect their rate limits — the app enforces a 1-second delay between requests.

## Project Structure

```
football_data_web/
├── main.py          # Entry point — orchestrates the full pipeline
├── scrap.py         # Scraping functions (team links, player stats)
├── clean_data.py    # Data cleaning, type conversion, and derived metrics
├── visualize.py     # Plot generation (scatter plots, bar charts)
├── config.py        # League URLs, constants, and default settings
├── pyproject.toml   # Project metadata and dependencies (managed by uv)
└── output/          # Generated plots saved here (created at runtime)
```

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
# Default: Lamine Yamal, La Liga
uv run python main.py

# Custom player and league
uv run python main.py --player "Vinicius Jr" --league la_liga
uv run python main.py --player "Erling Haaland" --league premier_league

# All options
uv run python main.py --help
```

### Available leagues

| Key              | League          |
|------------------|-----------------|
| `la_liga`        | La Liga         |
| `premier_league` | Premier League  |
| `bundesliga`     | Bundesliga      |
| `serie_a`        | Serie A         |
| `ligue_1`        | Ligue 1         |

## Output

Three plots are saved to the `output/` directory:

- **`plot_total_stats.png`** — Top forwards by total npxG+xA vs progressive carries, with the selected player highlighted
- **`plot_per90_stats.png`** — Same comparison normalized to per-90-minute stats
- **`plot_player_vs_peers.png`** — Bar chart comparing the player's per-90 numbers against the top-forwards group average

A stat summary for the selected player is also printed to the terminal.
