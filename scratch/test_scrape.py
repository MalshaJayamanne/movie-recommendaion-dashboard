import requests
import re

movie_id = 19995 # Avatar
url = f"https://www.themoviedb.org/movie/{movie_id}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"--- Fetching TMDB Movie Page for ID {movie_id} ---")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print("Status Code:", r.status_code)
    if r.status_code == 200:
        html = r.text
        # Look for og:image
        match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
        if match:
            print("Found og:image using pattern 1:", match.group(1))
        else:
            # Try searching for other image tags
            match2 = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
            if match2:
                print("Found og:image using pattern 2:", match2.group(1))
            else:
                # Find any image with /t/p/
                images = re.findall(r'https://image.tmdb.org/t/p/[^"\']+', html)
                if images:
                    print("Found images with TMDB path:", images[:3])
                else:
                    print("No TMDB images found in HTML.")
except Exception as e:
    print("Error:", e)
