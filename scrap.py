import time
import lxml.html
import requests
from urllib.parse import urlparse

from config import REQUEST_DELAY


def make_request(url):
    """Make a rate-limited GET request and return the response."""
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    return requests.get(url)


def make_link_absolute(rel_url, current_url):
    """Convert a relative URL to an absolute URL using the current page's URL as base."""
    parsed = urlparse(current_url)
    if rel_url.startswith("/"):
        return f"{parsed.scheme}://{parsed.netloc}{rel_url}"
    elif rel_url.startswith("?"):
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{rel_url}"
    return rel_url


def get_team_links(league_url):
    """
    Scrape all team page URLs from a league standings page.

    Parameters:
        league_url (str): URL of the league stats page on fbref.com

    Returns:
        list[str]: Absolute URLs for each team's stats page
    """
    page = make_request(league_url).text
    root = lxml.html.fromstring(page)
    # The table ID changes by league/year; target the first overall standings table
    elements = root.xpath('//table[contains(@id,"_overall")]/tbody/tr/td[1]/a')
    return [make_link_absolute(el.get("href"), league_url) for el in elements if el.get("href")]


def get_player_data(team_url):
    """
    Scrape all player stats from a team's page.

    Parameters:
        team_url (str): URL of a team's stats page on fbref.com

    Returns:
        list[dict]: One dict per player with raw stat strings
    """
    page = make_request(team_url).text
    root = lxml.html.fromstring(page)

    meta_spans = root.xpath('//*[@id="meta"]/div/h1/span')
    team_name_raw = meta_spans[0].text if len(meta_spans) > 0 else ""
    league_text_raw = meta_spans[1].text if len(meta_spans) > 1 else ""

    players = root.xpath('//*[contains(@id,"stats_standard_")]//tbody//tr//th[@class="left "]')

    player_data = []
    for player in players:
        siblings = player.xpath('./following-sibling::td')
        if len(siblings) < 22:
            continue

        player_data.append({
            "team_raw": team_name_raw,
            "league_raw": league_text_raw,
            "name": player[0].text.strip() if player[0].text else "",
            "position": siblings[1].text,
            "age": siblings[2].text,
            "mins": siblings[5].text,
            "xg": siblings[15].text,
            "npxg": siblings[16].text,
            "xa": siblings[17].text,
            "prgc": siblings[19].text,
            "prgp": siblings[20].text,
            "prgr": siblings[21].text,
        })

    return player_data


def get_league_data(league_url):
    """
    Scrape all player data for every team in a league.

    Parameters:
        league_url (str): URL of the league stats page on fbref.com

    Returns:
        list[dict]: All players across all teams
    """
    team_urls = get_team_links(league_url)
    all_players = []
    for url in team_urls:
        all_players.extend(get_player_data(url))
    return all_players
