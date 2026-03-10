import pathlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


AGE_RANGE_ORDER = ["under 20", "20 - 25", "25 - 30", "over 30"]
AGE_PALETTE = {
    "under 20": "#e63946",
    "20 - 25": "#457b9d",
    "25 - 30": "#2a9d8f",
    "over 30": "#e9c46a",
}


def _highlight_player(ax, row, x_col, y_col, label_offset=(0.02, 0.02)):
    """Draw a star marker and name label for the selected player."""
    ax.scatter(
        row[x_col],
        row[y_col],
        marker="*",
        s=300,
        color="#e63946",
        zorder=5,
        linewidths=0.5,
        edgecolors="black",
        label=row["name"],
    )
    ax.annotate(
        row["name"],
        xy=(row[x_col], row[y_col]),
        xytext=(row[x_col] + label_offset[0], row[y_col] + label_offset[1]),
        fontsize=9,
        fontweight="bold",
        color="#e63946",
    )


def plot_total_stats(df_forwards, player_name, output_dir):
    """
    Scatter plot: xg+xa (x) vs progressive carries (y) for top La Liga forwards.
    The selected player is highlighted with a star marker.

    Parameters:
        df_forwards (pd.DataFrame): forwards-only DataFrame, top-n already filtered
        player_name (str): name of the player to highlight
        output_dir (str | Path): directory where the PNG will be saved

    Returns:
        pathlib.Path: path to the saved figure
    """
    output_path = pathlib.Path(output_dir) / "plot_total_stats.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.set_style("white")

    # Plot all forwards
    sns.scatterplot(
        data=df_forwards,
        x="xg_plus_xa",
        y="prgc",
        hue="age_range",
        hue_order=AGE_RANGE_ORDER,
        palette=AGE_PALETTE,
        s=80,
        alpha=0.8,
        ax=ax,
    )

    # Highlight selected player
    player_row = df_forwards[df_forwards["name"].str.contains(player_name, case=False, na=False)]
    if not player_row.empty:
        _highlight_player(ax, player_row.iloc[0], "xg_plus_xa", "prgc", label_offset=(0.1, 1.5))

    ax.set_xlabel("Non-penalty xG + xA (total)", fontsize=11)
    ax.set_ylabel("Progressive Carries (total)", fontsize=11)
    ax.set_title("La Liga Forwards – Attacking Contribution vs Progression", fontsize=13, pad=12)
    ax.legend(title="Age group")
    sns.despine()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")
    return output_path


def plot_per90_stats(df_forwards, player_name, output_dir):
    """
    Scatter plot: xg+xa per 90 (x) vs progressive carries per 90 (y).
    The selected player is highlighted with a star marker.

    Parameters:
        df_forwards (pd.DataFrame): forwards-only DataFrame, top-n already filtered
        player_name (str): name of the player to highlight
        output_dir (str | Path): directory where the PNG will be saved

    Returns:
        pathlib.Path: path to the saved figure
    """
    output_path = pathlib.Path(output_dir) / "plot_per90_stats.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.set_style("white")

    sns.scatterplot(
        data=df_forwards,
        x="xg_plus_xa_90",
        y="prgc_90",
        hue="age_range",
        hue_order=AGE_RANGE_ORDER,
        palette=AGE_PALETTE,
        s=80,
        alpha=0.8,
        ax=ax,
    )

    player_row = df_forwards[df_forwards["name"].str.contains(player_name, case=False, na=False)]
    if not player_row.empty:
        _highlight_player(ax, player_row.iloc[0], "xg_plus_xa_90", "prgc_90", label_offset=(0.005, 0.05))

    ax.set_xlabel("Non-penalty xG + xA per 90 mins", fontsize=11)
    ax.set_ylabel("Progressive Carries per 90 mins", fontsize=11)
    ax.set_title("La Liga Forwards – Attacking Contribution vs Progression (per 90)", fontsize=13, pad=12)
    ax.legend(title="Age group")
    sns.despine()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")
    return output_path


def plot_player_radar(summary, peer_means, output_dir):
    """
    Bar chart comparing a player's per-90 stats against the peer group average.

    Parameters:
        summary (dict): output of clean_data.player_summary()
        peer_means (dict): same keys as summary with mean values for the peer group
        output_dir (str | Path): directory where the PNG will be saved

    Returns:
        pathlib.Path: path to the saved figure
    """
    output_path = pathlib.Path(output_dir) / "plot_player_vs_peers.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats = ["prgc_90", "xg_plus_xa_90"]
    labels = ["Prog. Carries / 90", "xG+xA / 90"]

    player_vals = [summary[s] for s in stats]
    peer_vals = [peer_means[s] for s in stats]

    x = range(len(stats))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    bars_player = ax.bar([i - width / 2 for i in x], player_vals, width, label=summary["name"], color="#e63946", alpha=0.85)
    bars_peers = ax.bar([i + width / 2 for i in x], peer_vals, width, label="Top peers avg", color="#457b9d", alpha=0.85)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Value", fontsize=11)
    ax.set_title(f"{summary['name']} vs Top Forwards (per 90 mins)", fontsize=13, pad=12)
    ax.legend()
    sns.despine()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")
    return output_path
