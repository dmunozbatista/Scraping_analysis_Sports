import lxml.html
import time
import requests
from urllib.parse import urlparse
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import pathlib


plot_1 = pathlib.Path(__file__).parents[1] / "Lamine_Yamal/initial_plot.png"
plot_per90 = pathlib.Path(__file__).parents[1] / "Lamine_Yamal/plot_per90_minutes.png"
REQUEST_DELAY = 0.9
url = "https://fbref.com/en/comps/12/La-Liga-Stats"

def make_request(url):
    """
    Make a request to `url` and return the raw response.

    This function ensure that the domain matches what is expected and that the rate limit
    is obeyed.
    """
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    resp = requests.get(url)
    return resp


def make_link_absolute(rel_url, current_url):
    """
    Given a relative URL like "/abc/def" or "?page=2"
    and a complete URL like "https://example.com/1/2/3" this function will
    combine the two yielding a URL like "https://example.com/abc/def"

    Parameters:
        * rel_url:      a URL or fragment
        * current_url:  a complete URL used to make the request that contained a link to rel_url

    Returns:
        A full URL with protocol & domain that refers to rel_url.
    """
    url = urlparse(current_url)
    if rel_url.startswith("/"):
        return f"{url.scheme}://{url.netloc}{rel_url}"
    elif rel_url.startswith("?"):
        return f"{url.scheme}://{url.netloc}{url.path}{rel_url}"
    else:
        return rel_url
    

def get_team_links(url):
    standings_page = make_request(url).text
    root = lxml.html.fromstring(standings_page)
    all_teams_elements = root.xpath('//*[@id="results2023-2024121_overall"]/tbody/tr/td[1]/a')
    teams_lst = []
    for element in all_teams_elements:
        href = element.get("href")
        if href:
            complete_url = make_link_absolute(href, url)
            teams_lst.append(complete_url)
    return teams_lst

teams_urls = get_team_links(url)

url = "https://fbref.com/en/squads/53a2f082/Real-Madrid-Stats"
page = make_request(url).text
root = lxml.html.fromstring(page)
team_items = root.xpath('//*[@id="meta"]/div/h1/span')
league_text = team_items[1]
team_name = team_items[0]

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


def get_player_data(url):
    page = make_request(url).text
    root = lxml.html.fromstring(page)
    team_items = root.xpath('//*[@id="meta"]/div/h1/span')
    league_text = team_items[1].text
    team_name = team_items[0].text
    cleaned_league = clean_league_name(league_text)
    cleaned_name = clean_team_name(team_name)

    players = root.xpath('//*[@id="stats_standard_12"]//tbody//tr//th[@class="left "]')  # XPath to target the player elements

    player_data = []
    for player in players:
        player_root = player.xpath('./following-sibling::td')
        player_name = player[0].text.strip()  # Extract the text content of the player element and remove leading/trailing spaces
        mins = player_root[5].text
        npxg = player_root[16].text
        xa = player_root[17].text
        xg = player_root[15].text
        prgc = player_root[19].text # XPath to extract PrgC
        prgp = player_root[20].text  # XPath to extract PrgP
        prgr = player_root[21].text
        position = player_root[1].text
        age = player_root[2].text

        player_data.append({
            "team": cleaned_name,
            "league": cleaned_league,
            "name": player_name,
            "position": position,
            "npxg": npxg,
            "prgc": prgc,
            "prgp": prgp,
            "prgr": prgr,
            "xg": xg,
            "mins": mins,
            "age": age,
            "xa": xa
        })
    return player_data


def get_la_liga(url_la_liga):
    all_teams_url = get_team_links(url_la_liga)
    complete_la_liga_data = []
    for url_team in all_teams_url:
        team = get_player_data(url_team)
        complete_la_liga_data += team
    return complete_la_liga_data
        
la_liga_data = get_la_liga("https://fbref.com/en/comps/12/La-Liga-Stats")


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


# Plot for first analysis. Most generated expected goals and progressive carries
sns.set_style("white")

# Define the desired order for the age range categories
age_range_order = ["under 20", "20 - 25", "25 - 30", "over 30"]
first_la_liga_plot = sns.scatterplot(data=top_15_prgc, x="xg_plus_xa", y="prgc", hue="age_range", hue_order=age_range_order)
first_la_liga_plot.legend(title='Age')
first_la_liga_plot.set(xlabel="Expected goals plus expected assists", ylabel="Progressive carries")
first_la_liga_plot.text(9, 129, "Sávio")
first_la_liga_plot.text(12, 130, "Rodrygo")
first_la_liga_plot.text(10.2, 95, "Vinicius")
first_la_liga_plot.text(6.5, 91, "Greenwood")
first_la_liga_plot.text(8.2, 89, "N. Williams")
first_la_liga_plot.text(8.2, 80, "Yamal")
first_la_liga_plot.text(12, 65, "Bellingham")
sns.despine()

plt.savefig(plot_1)


# Analysis with statistics per 90 minutes

df_90 = pd.DataFrame(la_liga_data)
df_90["prgc"] = pd.to_numeric(df["prgc"])

df_90["mins"] = df_90["mins"].str.replace(',', '').astype(float)

df_90 = df_90[df_90["mins"] > 1000]

df_90["npxg"] = pd.to_numeric(df_90["npxg"], errors='coerce')
df_90["xa"] = pd.to_numeric(df_90["xa"], errors='coerce')
df_90["xg"] = pd.to_numeric(df_90["xg"], errors='coerce')
df_90["prgp"] = pd.to_numeric(df_90["prgp"], errors='coerce')
df_90["prgr"] = pd.to_numeric(df_90["prgr"], errors='coerce')

df_90["npxg_90"] = (df_90["npxg"] / df_90["mins"]) * 90

df_90["xa_90"] = (df_90["xa"] / df_90["mins"]) * 90

df_90["prgc_90"] = (df_90["prgc"] / df_90["mins"]) * 90

df_90["xg_plus_xa_90"] = ((df_90["npxg"] + df_90["xa"])/ df_90["mins"]) * 90

df_90["forward"] = df_90["position"].apply(determine_forward)

df_90["age_range"] = df_90["age"].apply(determine_age_range)

df_90_sorted = df_90.sort_values(by="prgc_90", ascending=False)

df_forwards_90 = df_90_sorted[df_90_sorted["forward"]==True]

top_10_per_90 = df_forwards_90.head(10)

sns.set_style("white")

# Define the desired order for the age range categories
age_range_order = ["under 20", "20 - 25", "25 - 30", "over 30"]
first_la_liga_plot = sns.scatterplot(data=top_10_per_90, x="xg_plus_xa_90", y="prgc_90", hue="age_range", hue_order=age_range_order)
first_la_liga_plot.legend(title='Age')
first_la_liga_plot.set(xlabel="Expected goals plus expected assists per 90 mins", ylabel="Progressive carries per 90 mins")
# first_la_liga_plot.text(9, 129, "Sávio")
first_la_liga_plot.text(0.52, 6.05, "Rodrygo")
first_la_liga_plot.text(0.66, 6, "Vinicius")
# first_la_liga_plot.text(6.5, 91, "Greenwood")
first_la_liga_plot.text(0.42, 5.05, "N. Williams")
first_la_liga_plot.text(0.52, 4.95, "Yamal")
first_la_liga_plot.text(0.61, 4.3, "Brahim")
sns.despine()
plt.savefig(plot_per90)