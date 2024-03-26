import lxml.html
import time
import requests
from urllib.parse import urlparse
from clean_data import clean_league_name, clean_team_name


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
    """
    Use xpaths to retrieve all team links. It only requires the web page main link

    Input:
        url (str): main webpage with football stats of La Liga
    
    Return:
        team_lst (list): list with all teams url of La Liga
    """
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

def get_player_data(url):
    """
    Given a team url, get all the players relevant data using xpaths

    Input:
        url (str): team url
    
    Return:
        player_data (list): list of dictionaries to easily transform to dataframe
    """
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
    """
    Give La liga url and retrieve all the information. It works for differerent
    leagues too

    Inputs:
        url_la_liga (str): La liga url

    Return:
        complete_la_liga_data (list): each element is a team data
    """
    all_teams_url = get_team_links(url_la_liga)
    complete_la_liga_data = []
    for url_team in all_teams_url:
        team = get_player_data(url_team)
        complete_la_liga_data += team
    return complete_la_liga_data
        
la_liga_data = get_la_liga("https://fbref.com/en/comps/12/La-Liga-Stats")

