import requests

keys = [
    "1f54bd990f1ed6bfd39d1148d8c2909c",
    "e44a80695de9315682613b52d3a312df",
    "4e21c32d8d3f1cc3cb341c2b5bc1a5f4",
    "a3d9eb01d4ad82d97ad3e4744e9ee605",
    "f24f40b1c2430568559de23e35d56776"
]

movie_id = 19995 # Avatar

print("--- Testing More TMDB API Keys ---")
for k in keys:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={k}"
    try:
        r = requests.get(url, timeout=5)
        print(f"Key {k[:5]}... Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Success for key", k)
            print("Title:", data.get("title"))
            print("Poster Path:", data.get("poster_path"))
            break
    except Exception as e:
        print(f"Error: {e}")
