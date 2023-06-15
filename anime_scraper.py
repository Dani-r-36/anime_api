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
    """opens bbc website for extraction"""
    with urlopen(url) as page:
        html_bytes = page.read()
        html = html_bytes.decode("utf_8")
    return html

def parse_anime(url):
    try:
        html = get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except URLError as err:
        print(err)
        return "error"

def get_anime_similar(soup, query):
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
    found = False
    while found == False:
        for anime in animes:
            if query == anime:
                return animes_url[animes.index(anime)], anime
            if int(fuzz.partial_ratio(query, anime)) > 86:
                return animes_url[animes.index(anime)], anime
        return None, None

def extract_anime_info(soup, anime_title):
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
    if query == None or query == '':
            raise ValueError
    if " " in query:
        url_query = query.replace(" ", "%20")
    else:
        url_query= query
    return url_query

def top_anime_extract(top_soup):
    anime_list = []
    anime_urls = []
    type_list = []
    eps_list = []
    start_list = []
    end_list = []
    score_list = []
    top_anime = top_soup.select("tr.ranking-list")
    for anime in top_anime:
        anime_name = anime.select("h3.hoverinfo_trigger.fl-l.fs14.fw-b.anime_ranking_h3")
        anime_name = anime_name[0].find("a")
        anime_url = anime_name["href"]
        anime_name = anime_name.text
        anime_details = anime.select("div.information.di-ib.mt4")[0].text.strip().split('\n')
        anime_year = anime_details[1].strip().split('\n')
        start_year, end_year = anime_year[0].split(' - ')
        start_year = start_year.split()[-1]
        end_year = end_year.split()[-1]
        type = anime_details[0].strip().split('\n')
        type, eps = type[0].split('(')
        eps, temp = eps.split(" ")
        score = anime.select("span.text.on.score-label.score-9")
        score = score[0].text
        anime_list.append(anime_name)
        anime_urls.append(anime_url)
        type_list.append(type)
        eps_list.append(eps)
        start_list.append(start_year)
        end_list.append(end_year)
        score_list.append(score)
    

if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=5001)

    top = parse_anime("https://myanimelist.net/topanime.php")
    top_anime_extract(top)
    # query = input("genre request")
    # genre_soup = parse_anime(ANIME_HOME)
    # anime_genres_url, all_anime_genres, requested_genre = get_anime_genre(genre_soup, query)
    # anime_genre_soup = parse_anime(f"{ANIME_DEFAULT}{anime_genres_url}")
    # anime_genre_urls, anime_genres = extract_anime_genre_info(anime_genre_soup,requested_genre)
