import re
import pandas as pd


def clean_league_name(league_raw):
    """Strip parentheses from league names like '(La Liga)' -> 'La Liga'."""
    parts = re.findall(r'[^()]+', league_raw or "")
    return "".join(parts).strip()


def clean_team_name(team_raw):
    """
    Extract team name from fbref header text like '2023-2024 Real Madrid Stats'.
    Returns 'Real Madrid'.
    """
    words = (team_raw or "").split()[1:]  # drop the season year
    name_words = []
    for word in words:
        if word == "Stats":
            break
        name_words.append(word)
    return " ".join(name_words)


def _is_forward(position_str):
    """Return True if any position token starts with 'F'."""
    if not position_str:
        return False
    return any(p.strip().startswith("F") for p in position_str.split(","))


def _age_range(age_str):
    """Bin age (fbref format '17-200') into a readable range label."""
    if not age_str:
        return "Unknown"
    try:
        age = int(age_str.split("-")[0])
    except ValueError:
        return "Unknown"
    if age <= 20:
        return "under 20"
    elif age <= 25:
        return "20 - 25"
    elif age <= 30:
        return "25 - 30"
    return "over 30"


def build_dataframe(raw_data):
    """
    Convert raw scraped dicts into a clean, typed DataFrame.

    Adds derived columns:
        - team, league         : cleaned name strings
        - forward              : bool, True if player plays as a forward
        - age_range            : binned age label
        - xg_plus_xa           : npxg + xa (total attacking contribution)
        - mins_played          : minutes as int (NaN rows dropped)
        - prgc_90, xg_plus_xa_90: per-90-minute versions of key stats

    Parameters:
        raw_data (list[dict]): output of scrap.get_league_data()

    Returns:
        pd.DataFrame
    """
    df = pd.DataFrame(raw_data)

    df["team"] = df["team_raw"].apply(clean_team_name)
    df["league"] = df["league_raw"].apply(clean_league_name)
    df.drop(columns=["team_raw", "league_raw"], inplace=True)

    numeric_cols = ["npxg", "xa", "xg", "prgc", "prgp", "prgr", "mins"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["mins", "npxg", "xa", "prgc"], inplace=True)
    df = df[df["mins"] > 0].copy()

    df["forward"] = df["position"].apply(_is_forward)
    df["age_range"] = df["age"].apply(_age_range)
    df["xg_plus_xa"] = df["npxg"] + df["xa"]
    df["prgc_90"] = df["prgc"] / df["mins"] * 90
    df["xg_plus_xa_90"] = df["xg_plus_xa"] / df["mins"] * 90

    return df


def filter_forwards(df):
    """Return only rows where position includes a forward role."""
    return df[df["forward"]].copy()


def get_top_by_prgc(df, n=15):
    """Return the top-n forwards sorted by total progressive carries."""
    return df.sort_values("prgc", ascending=False).head(n)


def get_top_by_prgc_90(df, n=10):
    """Return the top-n forwards sorted by progressive carries per 90 mins."""
    return df.sort_values("prgc_90", ascending=False).head(n)


def player_summary(df, player_name):
    """
    Return a dict of key stats for a single player.

    Parameters:
        df (pd.DataFrame): full cleaned DataFrame (not filtered)
        player_name (str): exact player name as it appears in the data

    Returns:
        dict or None if player not found
    """
    row = df[df["name"] == player_name]
    if row.empty:
        # Try a case-insensitive partial match
        row = df[df["name"].str.contains(player_name, case=False, na=False)]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "name": row["name"],
        "team": row["team"],
        "position": row["position"],
        "age": row["age"],
        "mins": int(row["mins"]),
        "xg": round(row["xg"], 2),
        "npxg": round(row["npxg"], 2),
        "xa": round(row["xa"], 2),
        "xg_plus_xa": round(row["xg_plus_xa"], 2),
        "prgc": int(row["prgc"]),
        "prgp": int(row["prgp"]),
        "prgc_90": round(row["prgc_90"], 2),
        "xg_plus_xa_90": round(row["xg_plus_xa_90"], 2),
    }
