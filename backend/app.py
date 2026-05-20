import os
import re
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from recommendation import MovieRecommender
from flask_cors import CORS
import pandas as pd
import pickle


app = Flask(__name__)
CORS(app)

# Initialize recommendation engine
recommender = MovieRecommender()

# Set up paths for frontend assets
# Sibling of backend/ is frontend/
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# File path for poster image cache
POSTER_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'poster_cache.json')

# Load poster cache
poster_cache = {}
if os.path.exists(POSTER_CACHE_PATH):
    try:
        with open(POSTER_CACHE_PATH, 'r', encoding='utf-8') as f:
            poster_cache = json.load(f)
    except Exception:
        poster_cache = {}

def save_poster_cache():
    try:
        with open(POSTER_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(poster_cache, f)
    except Exception as e:
        print("[Server] Warning: Failed to save poster cache:", e)

def fetch_poster(movie_id):
    """
    Key-free dynamic web scraper fetching Open Graph images from public TMDB pages.
    Falls back to a cinematic gradient card if scraping fails.
    """
    movie_id_str = str(movie_id)
    if movie_id_str in poster_cache:
        return poster_cache[movie_id_str]
        
    url = f"https://www.themoviedb.org/movie/{movie_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            html = r.text
            # Look for og:image meta tag
            match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
            if match:
                img_url = match.group(1)
                poster_cache[movie_id_str] = img_url
                save_poster_cache()
                return img_url
            
            # Alternative layout match
            match2 = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
            if match2:
                img_url = match2.group(1)
                poster_cache[movie_id_str] = img_url
                save_poster_cache()
                return img_url
    except Exception as e:
        print(f"[Server] Failed to scrape poster for TMDB Movie ID {movie_id}: {e}")
        
    # Return placeholder flag if scraping fails
    return f"placeholder-{movie_id}"

# PAGE ROUTING ========

@app.route('/')
def home():
    """Serves the index landing page from the frontend directory."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/dashboard')
def dashboard():
    """Serves the main application dashboard from the frontend directory."""
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serves static files (styles, scripts, assets) dynamically."""
    return send_from_directory(FRONTEND_DIR, path)

# ====== API ENDPOINTS  ======

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Returns a full list of all movie titles for frontend autocomplete."""
    titles = recommender.get_all_titles()
    return jsonify(titles)

@app.route('/api/recommend', methods=['POST'])
def recommend_movies():
    """
    Accepts search query and returns recommended movies with complete metadata,
    including dynamically scraped poster URLs.
    """
    data = request.get_json()
    if not data or 'movie' not in data:
        return jsonify({"error": "Missing 'movie' field in request JSON"}), 400
        
    query_movie = data['movie']
    print(f"[API] Received recommendation request for: '{query_movie}'")
    
    recs = recommender.recommend(query_movie, num_recommendations=6)
    
    if not recs:
        return jsonify([])
        
    # Populate posters for the recommendations
    for movie in recs:
        movie['poster_url'] = fetch_poster(movie['movie_id'])
        
    return jsonify(recs)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Generates complex aggregated metrics across the clean movie dataset
    to power four rich frontend dashboard charts.
    """
    df = recommender.df
    if df is None:
        return jsonify({"error": "Dataset not loaded"}), 500
        
    # 1. Genre Distribution Chart (Top 10 Genres)
    genres_series = df['genres_display'].dropna().str.split(', ')
    all_genres = []
    for g_list in genres_series:
        if isinstance(g_list, list):
            all_genres.extend([g.strip() for g in g_list if g.strip()])
            
    from collections import Counter
    genre_counts = Counter(all_genres)
    top_genres = genre_counts.most_common(10)
    genre_labels = [g[0] for g in top_genres]
    genre_data = [g[1] for g in top_genres]
    
    # 2. Top Rated Masterpieces (Top 10 sorted by vote_average, minimum 1000 votes)
    top_rated_df = df[df['vote_count'] >= 1000].sort_values(by='vote_average', ascending=False).head(10)
    top_rated_movies = []
    for _, row in top_rated_df.iterrows():
        top_rated_movies.append({
            'title': row['title'],
            'rating': float(row['vote_average']),
            'votes': int(row['vote_count'])
        })
        
    # 3. Popularity Trends Scatter Data (Top 100 popular movies)
    scatter_df = df.sort_values(by='popularity', ascending=False).head(100)
    scatter_data = []
    for _, row in scatter_df.iterrows():
        scatter_data.append({
            'x': float(row['vote_average']),
            'y': float(row['popularity']),
            'title': str(row['title'])
        })
        
    # 4. Yearly Movie Release Trends (From 1990 - 2016)
    trend_df = df[(df['release_year'] >= 1990) & (df['release_year'] <= 2016)]
    yearly_counts = trend_df.groupby('release_year').size().reset_index(name='count')
    yearly_counts = yearly_counts.sort_values(by='release_year')
    years = yearly_counts['release_year'].tolist()
    counts = yearly_counts['count'].tolist()
    
    analytics_payload = {
        'genres': {
            'labels': genre_labels,
            'values': genre_data
        },
        'top_rated': top_rated_movies,
        'scatter': scatter_data,
        'trends': {
            'years': years,
            'counts': counts
        }
    }
    
    return jsonify(analytics_payload)

if __name__ == '__main__':
    print("[Server] Starting MovieMind AI Backend Flask Server...")
    app.run(host='127.0.0.1', port=5000, debug=True)
