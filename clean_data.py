import pandas as pd
import re
from scrap import la_liga_data


def clean_league_name(league_text):
    """
    League names are enclosed in parenthesis, this function cleans those names

    Inputs:
        league_text (str): text retrieved from html code. For example; "(La Liga)"

    Return:
        cleaned_league (str): league name without parenthesis
    """
    result = re.findall(r'[^()]+', league_text)
    cleaned_league = ''.join(result)
    return cleaned_league


def clean_team_name(team_name):
    """
    Text retrieved with xpath has different elements. Season year "2023-2024",
    team name (can have more than one word), and the following elements start with
    the word "Stats". We only want the team name

    Inputs:
        team_name (str): text retrieved with xpath from html code

    Return:
        team (str): cleaned text that only has the name. For example: "Real Madrid"
    """
    name = team_name.split()[1:]
    team = ""
    for word in name:
        if word == "Stats":
            break
        team += " " + word
    team = team[1:]
    return team



# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(la_liga_data)
df["prgc"] = pd.to_numeric(df["prgc"])
df_sorted = df.sort_values(by='prgc', ascending=False)

def determine_forward(observation):
    positions = observation.split(",")  # Access the position string directly
    for position in positions:
        if position[0] == "F":
            return True
    return False

def determine_age_range(observation):
    if observation is None:
        return "Unknown"  # Or any other appropriate value for missing data
    age_str = observation.split("-")[0]  # Extract the first two digits representing years
    age = int(age_str)
    if age <= 20:
        return "under 20"
    elif age > 20 and age <= 25:
        return "20 - 25"
    elif age > 25 and age <= 30:
        return "25 - 30"
    else:
        return "over 30"

# Apply the function to each value in the "position" column
df_sorted["npxg"] = df_sorted["npxg"].astype(float)
df_sorted["xa"] = df_sorted["xa"].astype(float)
df_sorted["xg_plus_xa"] = df_sorted["npxg"] + df_sorted["xa"]
df_sorted["forward"] = df_sorted["position"].apply(determine_forward)
df_sorted["age_range"] = df_sorted["age"].apply(determine_age_range)
df_forwards = df_sorted[df_sorted["forward"]]

top_15_prgc = df_forwards.head(15)
