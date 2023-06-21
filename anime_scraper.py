"""This script is used to scrap myanimelist site for anime details"""
from urllib.request import urlopen
from urllib.error import URLError
import psycopg2
import psycopg2.extras
import re
import json
from bs4 import BeautifulSoup
from rich.console import Console
from rapidfuzz import fuzz
from flask import Flask, current_app, request, jsonify, render_template

app = Flask(__name__)
console = Console()

ANIME_SEARCH = "https://myanimelist.net/anime.php?cat=anime&q="
ANIME_HOME = "https://myanimelist.net/anime.php"
ANIME_DEFAULT = "https://myanimelist.net"

def get_html(url):
    """opens website for extraction"""
    with urlopen(url) as page:
        html_bytes = page.read()
        html = html_bytes.decode("utf_8")
    return html

def parse_anime(url):
    """Uses beautifulsoup to extract the html from the site"""
    try:
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except URLError as err:
        print(err)
        return "error"

def get_anime_similar(soup, query):
    """Not used function"""
    """scapes all anime similar to queried function"""
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
    anime_url, anime_title = check_request(animes_title, animes_url, "anime", query)
    if anime_title == None:
        return None, animes_title
    return anime_url, anime_title

def check_request(animes, animes_url, type_request, query):
    """checks how similar query is to list of similar anime or anime generes"""
    found = False
    while found == False:
        for anime in animes:
            if query == anime:
                return animes_url[animes.index(anime)], anime
            if int(fuzz.partial_ratio(query, anime)) > 86:
                return animes_url[animes.index(anime)], anime
        return None, None

def extract_anime_info(soup, anime_title):
    """extracts anime details from html text"""
    details = soup.find("div", {"class": "stats-block po-r clearfix"})
    score_div = details.find("div", {"class": "score-label"})
    score = score_div.text
    ranked_span = details.find("span", {"class": "numbers ranked"})
    ranked = ranked_span.strong.text
    popular_span = details.find("span", {"class": "numbers popularity"})
    popular = popular_span.strong.text
    paragraph_p = soup.find("p", {"itemprop":"description"})
    paragraph = paragraph_p.text
    anime_data = {
        "name" : anime_title,
        "synopsis" : paragraph,
        "score":score,
        "rank":ranked,
        "popularity":popular
    }
    print(anime_data)
    return json.dumps(anime_data)

def get_anime_genre(soup, query):
    """extracts all genres from html and urls"""
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
    anime_url, actual_genre = check_request(anime_genre_split, anime_genre_link, "genre", query)
    return anime_url, anime_genre_split, actual_genre

def extract_anime_genre_info(animes_soup, query):
    """extracts animes from specific genre"""
    anime_list = []
    anime_urls = []
    genre_animes = animes_soup.select("div.js-anime-category-producer.seasonal-anime.js-seasonal-anime.js-anime-type-all.js-anime-type-1")
    for anime in genre_animes:
        anime_details_better = anime.select("h2.h2_anime_title")
        url = anime_details_better[0].find("a")
        anime_list.append(anime_details_better[0].text)
        anime_urls.append(url["href"])
    return anime_urls, anime_list

def parse_query(query):
    """replaces space with html space %20"""
    if query == None or query == '':
            raise ValueError
    if " " in query:
        url_query = query.replace(" ", "%20")
    else:
        url_query= query
    return url_query

def top_anime_extract(top_soup):
    """extracts top 50 anime and details"""
    anime_info = {}
    anime_list = []
    top_anime = top_soup.select("tr.ranking-list")
    for anime in top_anime:
        position = int(anime.select("td.rank.ac")[0].text.strip())
        anime_name = anime.select("h3.hoverinfo_trigger.fl-l.fs14.fw-b.anime_ranking_h3")
        anime_name = anime_name[0].find("a")
        anime_url = anime_name["href"]
        anime_name = anime_name.text
        anime_details = anime.select("div.information.di-ib.mt4")[0].text.strip().split('\n')
        score = anime.select("div.js-top-ranking-score-col.di-ib.al")
        if len(score) >0:
            score = score[0].text
        start_year, end_year, type_genre, eps = additional_top_anime(anime_details)
        anime_info = {"anime":anime_name, "anime_url": anime_url, "type_genre": type_genre,
                      "eps": eps, "start": start_year, "end": end_year, "score": score}
        anime_list.append(anime_info)
    return anime_list

def additional_top_anime(anime_details):
    """formats top 50 anime details"""
    anime_year = anime_details[1].strip().split('\n')
    start_year, end_year = anime_year[0].split(' - ')
    start_year = start_year.split()[-1]
    end_year = end_year.split()[-1]
    type_genre = anime_details[0].strip().split('\n')
    type_genre, eps = type_genre[0].split('(')
    eps, temp = eps.split(" ")
    return start_year, end_year, type_genre, eps

if __name__ == "__main__":
    top = parse_anime("https://myanimelist.net/topanime.php")
    top_anime_extract(top)
    # query = input("genre request")
    # genre_soup = parse_anime(ANIME_HOME)
    # anime_genres_url, all_anime_genres, requested_genre = get_anime_genre(genre_soup, query)
    # anime_genre_soup = parse_anime(f"{ANIME_DEFAULT}{anime_genres_url}")
    # anime_genre_urls, anime_genres = extract_anime_genre_info(anime_genre_soup,requested_genre)
