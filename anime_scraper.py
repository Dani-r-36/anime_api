from urllib.request import urlopen
import psycopg2
import psycopg2.extras
import re
from bs4 import BeautifulSoup
from rich.console import Console
from rapidfuzz import fuzz

console = Console()

ANIME_SEARCH = "https://myanimelist.net/anime.php?cat=anime&q="
ANIME_HOME = "https://myanimelist.net/anime.php"
ANIME_DEFAULT = "https://myanimelist.net"

def get_html(url):
    """opens bbc website for extraction"""
    with urlopen(url) as page:
        html_bytes = page.read()
        html = html_bytes.decode("utf_8")
    return html

def parse_anime(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_anime_similar(soup):
    animes_title = []
    animes_url = []
    animes = soup.select("a.hoverinfo_trigger")
    for anime in animes:
        title = anime.text
        if '\n' not in title:
            animes_title.append(title)
        url = anime.get('href')
        if url not in animes_url:
            animes_url.append(anime.get('href'))
    anime_url = check_request(animes_title, animes_url, "anime")
    return anime_url

def check_request(animes, animes_url, type_request):
    console.print(animes)
    found = False
    while found == False:
        anime_request = input(f"Enter {type_request} from list\n")
        for anime in animes:
            if int(fuzz.partial_ratio(anime_request, anime)) > 85:
                found = True
                break
    return animes_url[animes.index(anime)]

def extract_anime_info(soup):
    details = soup.find("div", {"class": "stats-block po-r clearfix"})
    score_div = details.find("div", {"class": "score-label"})
    score = score_div.text
    ranked_span = details.find("span", {"class": "numbers ranked"})
    ranked = ranked_span.strong.text
    popular_span = details.find("span", {"class": "numbers popularity"})
    popular = popular_span.strong.text
    paragraph_p = soup.find("p", {"itemprop":"description"})
    paragraph = paragraph_p.text
    print(paragraph)
    print(score, ranked, popular)

def get_anime_genre(soup):
    anime_genre_split = []
    anime_genre_link = []
    genres = soup.select('div.normal_header.pt24.mb0')
    for genre in genres:
        heading = genre.text
        if heading == "Genres" or heading == "Themes":
            genre_content = genre.find_next_sibling('div')
            link = genre_content.select('a.genre-name-link')
            href_link = [a['href'] for a in link]
            genre_split = [s.strip() + ')' for s in re.split(r'\)(?=[A-Z])', genre_content.text) if s.strip()]
            anime_genre_split.extend(genre_split)
            anime_genre_link.extend(href_link)
    anime_url = check_request(anime_genre_split, anime_genre_link, "genre")
    return anime_url

def extract_anime_genre_info(animes_soup):
    anime_list = []
    anime_urls = []
    genre_animes = animes_soup.select("div.js-anime-category-producer.seasonal-anime.js-seasonal-anime.js-anime-type-all.js-anime-type-1")
    for anime in genre_animes:
        anime_details_better = anime.select("h2.h2_anime_title")
        url = anime_details_better[0].find("a")
        anime_list.append(anime_details_better[0].text)
        anime_urls.append(url["href"])
    anime_url = check_request(anime_list, anime_urls, "anime")
    return anime_url

if __name__ == "__main__":
    # requested_anime = input("Enter anime to search\n")
    # search_url = f"{ANIME_SEARCH}{requested_anime}"
    # soup = parse_anime(search_url)
    # anime_url = get_anime_similar(soup)
    # anime_soup = parse_anime(anime_url)
    # extract_anime_info(anime_soup)

    genre_soup = parse_anime(ANIME_HOME)
    anime_genres_url = get_anime_genre(genre_soup)
    anime_genre_soup = parse_anime(f"{ANIME_DEFAULT}{anime_genres_url}")
    anime_genre_url = extract_anime_genre_info(anime_genre_soup)
    anime_genre_soup = parse_anime(anime_genre_url)
    extract_anime_info(anime_genre_soup)