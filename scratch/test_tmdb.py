import requests

keys = [
    "8213f92e3cf5d44cc27788540d5c1d67",  # Famous public key
    "c860c2d3ca4523c14d9be25b3ab38b89",  # Another common public key
    "19f84e11932abbda55a6d22d42d47ad5"   # Third key
]

movie_id = 19995 # Avatar

print("--- Testing TMDB API Keys ---")
for k in keys:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={k}"
    try:
        r = requests.get(url, timeout=5)
        print(f"Key {k[:5]}... Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Successfully retrieved data!")
            print("Title:", data.get("title"))
            print("Poster Path:", data.get("poster_path"))
            print("Overview:", data.get("overview")[:100] + "...")
            break
    except Exception as e:
        print(f"Error for key {k[:5]}...: {e}")
