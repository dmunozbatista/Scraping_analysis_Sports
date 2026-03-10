"""
football_data_web – main entry point

Usage:
    python main.py
    python main.py --player "Vinicius Jr" --league premier_league
    python main.py --player "Lamine Yamal" --output results/

Run `python main.py --help` for all options.
"""
import argparse
import sys

import pandas as pd

from config import LEAGUE_URLS, DEFAULT_LEAGUE, DEFAULT_PLAYER, OUTPUT_DIR
from scrap import get_league_data
from clean_data import build_dataframe, filter_forwards, get_top_by_prgc, get_top_by_prgc_90, player_summary
from visualize import plot_total_stats, plot_per90_stats, plot_player_radar


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape fbref.com and visualize player stats.")
    parser.add_argument(
        "--player",
        default=DEFAULT_PLAYER,
        help=f"Player name to highlight (default: '{DEFAULT_PLAYER}')",
    )
    parser.add_argument(
        "--league",
        default=DEFAULT_LEAGUE,
        choices=list(LEAGUE_URLS.keys()),
        help=f"League to scrape (default: {DEFAULT_LEAGUE})",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR,
        help=f"Directory to save plots (default: '{OUTPUT_DIR}')",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=15,
        help="Number of top forwards to include in scatter plots (default: 15)",
    )
    return parser.parse_args()


def print_summary(summary):
    print("\n" + "=" * 45)
    print(f"  {summary['name']}  ({summary['team']})")
    print("=" * 45)
    print(f"  Position : {summary['position']}")
    print(f"  Age      : {summary['age']}")
    print(f"  Minutes  : {summary['mins']}")
    print(f"  xG       : {summary['xg']}")
    print(f"  npxG     : {summary['npxg']}")
    print(f"  xA       : {summary['xa']}")
    print(f"  xG+xA    : {summary['xg_plus_xa']}")
    print(f"  PrgC     : {summary['prgc']}  ({summary['prgc_90']} / 90)")
    print(f"  xG+xA/90 : {summary['xg_plus_xa_90']}")
    print("=" * 45 + "\n")


def main():
    args = parse_args()
    league_url = LEAGUE_URLS[args.league]

    # ── 1. Scrape ────────────────────────────────────────────────────────────
    print(f"\nScraping {args.league} data from fbref.com …")
    raw_data = get_league_data(league_url)

    # ── 2. Clean ─────────────────────────────────────────────────────────────
    print("\nCleaning data …")
    df = build_dataframe(raw_data)
    df_forwards = filter_forwards(df)

    # ── 3. Player summary ────────────────────────────────────────────────────
    summary = player_summary(df, args.player)
    if summary is None:
        print(f"\nError: Player '{args.player}' not found in the scraped data.")
        print("Available players (sample):", df["name"].sample(min(10, len(df))).tolist())
        sys.exit(1)

    print_summary(summary)

    # ── 4. Prepare peer group ────────────────────────────────────────────────
    # Make sure the selected player is always in the plot even if not in top-n
    top_total = get_top_by_prgc(df_forwards, n=args.top_n)
    top_per90 = get_top_by_prgc_90(df_forwards, n=args.top_n)

    def ensure_player(base_df, full_df, player_name):
        if not base_df["name"].str.contains(player_name, case=False, na=False).any():
            player_row = full_df[full_df["name"].str.contains(player_name, case=False, na=False)]
            if not player_row.empty:
                return pd.concat([base_df, player_row], ignore_index=True)
        return base_df

    top_total = ensure_player(top_total, df_forwards, args.player)
    top_per90 = ensure_player(top_per90, df_forwards, args.player)

    # Peer means (top-n, excluding the selected player)
    peers = df_forwards[~df_forwards["name"].str.contains(args.player, case=False, na=False)]
    top_peers = get_top_by_prgc_90(peers, n=args.top_n)
    peer_means = {
        "prgc_90": round(top_peers["prgc_90"].mean(), 2),
        "xg_plus_xa_90": round(top_peers["xg_plus_xa_90"].mean(), 2),
    }

    # ── 5. Visualize ─────────────────────────────────────────────────────────
    print("Generating plots …")
    plot_total_stats(top_total, args.player, args.output)
    plot_per90_stats(top_per90, args.player, args.output)
    plot_player_radar(summary, peer_means, args.output)

    print(f"\nDone. Plots saved to '{args.output}/'")


if __name__ == "__main__":
    main()
