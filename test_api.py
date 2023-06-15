import json
from unittest.mock import patch
import unittest.mock as mock
import pytest
from urllib.error import URLError
from flask import jsonify
from api import app, search, parse_query
from anime_scraper import get_anime_similar, extract_anime_info, parse_anime
from bs4 import BeautifulSoup
import os

test_api = app.test_client()

def test_index():
    test_api = app.test_client()
    response=test_api.get("/")
    assert response.status_code == 200

@patch("api.extract_anime_info")
def test_stories_return_stories(mock_anime):
    test_api = app.test_client()
    mock_anime.return_value = {"anime":""}
    response = test_api.get("/anime/search?query=anime")
    data = response.json
    assert response.status_code == 200
    assert isinstance(data,dict)

def test_parse_query_invalid_query():
    with pytest.raises(ValueError):
        parse_query(None)
    with pytest.raises(ValueError):
        parse_query('')

def test_similar_anime():
    html = """
            <html>
                <body>
                    <a class="hoverinfo_trigger" href="https://example.com/anime1">Anime 1</a>
                </body>
            </html>
        """
    mock_soup = BeautifulSoup(html, 'html.parser')
    mock_query = "Anime 1"
    # Use the mock_soup object in your test case
    anime_url, anime_title = get_anime_similar(mock_soup, mock_query)
    assert anime_url == "https://example.com/anime1"
    assert anime_title == "Anime 1"


def test_anime_info():
    html = """
            <html>
                <body>
                <div class="stats-block po-r clearfix">
                        <div class="score-label score-8">8.35</div>
                    <div class="di-ib ml12 pl20 pt8">
                        <span class="numbers ranked" title="based on the top anime page. Please note that 'Not yet aired' and 'R18+' titles are excluded.">
                            Ranked 
                            <strong>#205</strong>
                        </span>
                        <span class="numbers popularity">
                            Popularity 
                            <strong>#364</strong>
                        </span>
                    </div>
                </div>
                <p itemprop="description">description of anime</p>
                </body>
            </html>
                    """
    mock_soup_anime = BeautifulSoup(html, 'html.parser')
    response = extract_anime_info(mock_soup_anime, "Anime 1")
    data = {
        "name" : "Anime 1",
        "synopsis" : "description of anime",
        "score":"8.35",
        "rank":"#205",
        "popularity":"#364"
    }
    assert response == json.dumps(data)

def test_parse_anime_invalid_query():
    with mock.patch("anime_scraper.get_html") as mock_get_html:
        mock_get_html.side_effect =URLError("Mocked URLError")
        result = parse_anime("https://fake.com")
        assert result == "error"
    # with pytest.raises(URLError):
    #     parse_anime('')
