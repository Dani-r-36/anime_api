from urllib.error import URLError
from flask import Flask, request, jsonify, render_template
from anime_scraper import parse_anime, get_anime_similar, extract_anime_genre_info, extract_anime_info, get_anime_genre, parse_query
from upload_db import get_anime_sql, error_message

ANIME_SEARCH = "https://myanimelist.net/anime.php?cat=anime&q="
ANIME_HOME = "https://myanimelist.net/anime.php"
ANIME_DEFAULT = "https://myanimelist.net"

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return render_template('home.html')

@app.route("/anime/search", methods=["GET"])
def search():
    try:
        query = request.args.get('query')
        url_query = parse_query(query)
        search_url = f"{ANIME_SEARCH}{url_query}"
        soup = parse_anime(search_url)
        if soup == "error":
            raise ValueError
        anime_url, anime_title = get_anime_similar(soup, query)
        if anime_url == None:
            return jsonify({"animes":anime_title})
        anime_soup = parse_anime(anime_url)
        if anime_soup == "error":
            raise ValueError
        return extract_anime_info(anime_soup, anime_title)
    
    except ValueError as err:
        print (err)
        return "Invalid query"

@app.route("/anime/allgenres", methods=["GET"])
def all_genres():
    genre_soup = parse_anime(ANIME_HOME)
    anime_genres_url, all_anime_genres, temp = get_anime_genre(genre_soup, None)
    return jsonify({"anime_genres": all_anime_genres})

@app.route("/anime/genre", methods=["GET"])
def genre_search():
    query = request.args.get('query')
    try:
        if query == None or query == '':
            raise ValueError
        if " " in query:
            anime_genres_url = query.replace(" ", "%20")
        genre_soup = parse_anime(ANIME_HOME)
        if genre_soup == "error":
            raise ValueError
        anime_genres_url, all_anime_genres, requested_genre = get_anime_genre(genre_soup, query)
        anime_genre_soup = parse_anime(f"{ANIME_DEFAULT}{anime_genres_url}")
        if anime_genre_soup == "error":
            raise ValueError
        anime_genre_urls, anime_genres = extract_anime_genre_info(anime_genre_soup,requested_genre)
        return jsonify({f"{query} animes": anime_genres})
    
    except ValueError as err:
        print (err)
        return ("Invalid query")
    
@app.route("/top_anime", methods=["GET"])
def top_anime():
    try:
        data = get_top_anime()
        if len(data) == 0:
            raise ValueError
        return data
    
    except ValueError as err:
        print (err)
        return ("Invalid query")
    
def get_top_anime():
    data = {}
    anime_list=[]
    unique_curs = get_anime_sql()
    for row in unique_curs:
        renamed_row = {
            'position': row['animes_id'], 
            'anime': row['anime'],
            'start_date_id': row['start_date_id'],
            'end_date_id': row['end_date_id'],
            'show_type_id': row['show_type_id'],
            'episodes': row['episodes'],
            'score': row['score']
        }
        anime_list.append(renamed_row)
    if len(anime_list) == 0:
        return error_message("oops no animes",404)
    data['Top 50 animes'] = anime_list
    return data
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)