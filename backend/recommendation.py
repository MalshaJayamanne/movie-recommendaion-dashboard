import pandas as pd
import pickle
import os

class MovieRecommender:
    def __init__(self):
        # Define paths relative to this file
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.movies_path = os.path.join(self.data_dir, 'movies_cleaned.csv')
        self.similarity_path = os.path.join(self.data_dir, 'similarity.pkl')
        
        self.df = None
        self.similarity = None
        self.load_data()
        
    def load_data(self):
        if not os.path.exists(self.movies_path):
            raise FileNotFoundError(f"Cleaned dataset not found at: {self.movies_path}. Please run train.py first.")
        if not os.path.exists(self.similarity_path):
            raise FileNotFoundError(f"Similarity matrix not found at: {self.similarity_path}. Please run train.py first.")
            
        print("[Recommender] Loading cleaned dataset...")
        self.df = pd.read_csv(self.movies_path)
        self.df['title_lower'] = self.df['title'].str.strip().str.lower()
        
        print("[Recommender] Loading similarity matrix...")
        with open(self.similarity_path, 'rb') as f:
            self.similarity = pickle.load(f)
            
        print(f"[Recommender] Successfully loaded data for {len(self.df)} movies.")

    def get_all_titles(self):
        """Returns a list of all movie titles in the dataset."""
        if self.df is None:
            return []
        return self.df['title'].tolist()

    def recommend(self, movie_title, num_recommendations=6):
        """
        Recommends similar movies based on cosine similarity.
        Includes case-insensitive lookups and partial matching.
        """
        if self.df is None or self.similarity is None:
            return []
            
        movie_title_clean = movie_title.strip().lower()
        
        # 1. Look for an exact match
        matches = self.df[self.df['title_lower'] == movie_title_clean]
        
        # 2. Smart fallback: Partial match
        if matches.empty:
            matches = self.df[self.df['title_lower'].str.contains(movie_title_clean, na=False)]
            if matches.empty:
                print(f"[Recommender] No matches found for query: '{movie_title}'")
                return []
            print(f"[Recommender] No exact match, found partial match: '{matches.iloc[0]['title']}'")
            
        # Use the first matched movie
        index = matches.index[0]
        matched_title = self.df.iloc[index]['title']
        print(f"[Recommender] Calculating recommendations for: '{matched_title}' (Index: {index})")
        
        # Get similarities for this movie index
        distances = self.similarity[index]
        
        # Sort indices by similarity score descending
        # Skip index itself if possible (or filter it out)
        sorted_similarities = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )
        
        recommendations = []
        for i in sorted_similarities:
            idx = i[0]
            score = float(i[1])
            
            # Skip the query movie itself
            if idx == index:
                continue
                
            row = self.df.iloc[idx]
            
            # Map columns safely
            recommendations.append({
                'movie_id': int(row['movie_id']),
                'title': str(row['title']),
                'overview': str(row['overview']) if pd.notna(row['overview']) else "",
                'tagline': str(row['tagline']) if pd.notna(row['tagline']) else "",
                'genres': str(row['genres_display']) if pd.notna(row['genres_display']) else "",
                'cast': str(row['cast_display']) if pd.notna(row['cast_display']) else "",
                'director': str(row['director_display']) if pd.notna(row['director_display']) else "",
                'vote_average': float(row['vote_average']) if pd.notna(row['vote_average']) else 0.0,
                'popularity': float(row['popularity']) if pd.notna(row['popularity']) else 0.0,
                'release_date': str(row['release_date']) if pd.notna(row['release_date']) else "",
                'release_year': int(row['release_year']) if pd.notna(row['release_year']) else 0,
                'similarity_score': round(score * 100, 1) # Represent as percentage
            })
            
            if len(recommendations) >= num_recommendations:
                break
                
        return recommendations
