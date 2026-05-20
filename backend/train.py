import pandas as pd
import numpy as np
import os
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def train_model():
    print("[MovieMind AI] ML Pipeline starting...")

    # Define paths
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    movies_path = os.path.join(data_dir, 'movies.csv')
    credits_path = os.path.join(data_dir, 'credits.csv')
    
    cleaned_movies_path = os.path.join(data_dir, 'movies_cleaned.csv')
    similarity_path = os.path.join(data_dir, 'similarity.pkl')

    if not os.path.exists(movies_path) or not os.path.exists(credits_path):
        print("[ERROR] Original datasets (movies.csv and credits.csv) not found in backend/data/")
        return

    print("[INFO] Loading raw datasets...")
    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)

    print(f"[INFO] Loaded {len(movies)} movies and {len(credits)} credits.")

    print("[INFO] Merging datasets on Title...")
    # Merge on title as in the jupyter notebook
    df = movies.merge(credits, on='title')
    print(f"[INFO] Merging complete. Shape: {df.shape}")

    print("[INFO] Cleaning and filling missing values...")
    # Fill missing columns
    for col in ['genres', 'keywords', 'cast', 'crew', 'overview', 'tagline']:
        df[col] = df[col].fillna('')

    # Helper function to convert JSON strings of lists to name list
    def convert_names(text):
        if not text:
            return []
        try:
            items = ast.literal_eval(text)
            return [item['name'] for item in items]
        except Exception:
            return []

    # Helper function to convert cast to top 3 actors
    def convert_top_cast(text):
        if not text:
            return []
        try:
            items = ast.literal_eval(text)
            return [item['name'] for item in items[:3]]
        except Exception:
            return []

    # Helper function to fetch the Director from crew
    def fetch_director(text):
        if not text:
            return []
        try:
            items = ast.literal_eval(text)
            for item in items:
                if item.get('job') == 'Director':
                    return [item.get('name')]
        except Exception:
            pass
        return []

    print("[INFO] Extracting metadata columns...")
    # Keep the readable clean columns for frontend dashboard and analytics
    df['genres_list'] = df['genres'].apply(convert_names)
    df['keywords_list'] = df['keywords'].apply(convert_names)
    df['cast_list'] = df['cast'].apply(convert_top_cast)
    df['director_list'] = df['crew'].apply(fetch_director)

    # Store comma-separated strings for frontend rendering
    df['genres_display'] = df['genres_list'].apply(lambda x: ", ".join(x))
    df['cast_display'] = df['cast_list'].apply(lambda x: ", ".join(x))
    df['director_display'] = df['director_list'].apply(lambda x: x[0] if x else "")

    print("[INFO] Collapsing spaces for ML Tag creation...")
    # ML pre-processing requires collapsing spaces (e.g. "Science Fiction" -> "ScienceFiction")
    # so that CountVectorizer treats them as a single token.
    def collapse_spaces(L):
        return [i.replace(" ", "") for i in L]

    genres_ml = df['genres_list'].apply(collapse_spaces)
    keywords_ml = df['keywords_list'].apply(collapse_spaces)
    cast_ml = df['cast_list'].apply(collapse_spaces)
    director_ml = df['director_list'].apply(collapse_spaces)

    # Split overview text into words
    overview_ml = df['overview'].apply(lambda x: x.split() if isinstance(x, str) else [])

    print("[INFO] Consolidated Tag generation...")
    # Generate combined tags list
    df['tags_list'] = overview_ml + genres_ml + keywords_ml + cast_ml + director_ml
    
    # Convert tags list into string and lowercase
    df['tags'] = df['tags_list'].apply(lambda x: " ".join(x).lower())

    # Build final cleaned dataframe for saving (keeping metadata for analytics & UI display)
    cleaned_df = df[[
        'movie_id', 'title', 'overview', 'tagline', 
        'genres_display', 'cast_display', 'director_display', 
        'vote_average', 'popularity', 'release_date', 'vote_count', 
        'tags'
    ]].copy()

    # Clean release date to extract release year for trends
    cleaned_df['release_year'] = pd.to_datetime(cleaned_df['release_date'], errors='coerce').dt.year
    cleaned_df['release_year'] = cleaned_df['release_year'].fillna(0).astype(int)

    print(f"[INFO] Saving cleaned dataset to {cleaned_movies_path}...")
    cleaned_df.to_csv(cleaned_movies_path, index=False)

    print("[INFO] Fitting CountVectorizer & computing Cosine Similarity...")
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(cleaned_df['tags']).toarray()
    
    print(f"[INFO] Feature vector shape: {vectors.shape}")
    
    similarity = cosine_similarity(vectors)
    print(f"[INFO] Similarity matrix shape: {similarity.shape}")

    print(f"[INFO] Saving similarity matrix model to {similarity_path}...")
    with open(similarity_path, 'wb') as f:
        pickle.dump(similarity, f)

    print("[SUCCESS] Model Training Complete and artifacts successfully generated!")

if __name__ == "__main__":
    train_model()
