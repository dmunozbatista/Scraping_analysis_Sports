import lxml.html
import time
import requests
from urllib.parse import urlparse

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