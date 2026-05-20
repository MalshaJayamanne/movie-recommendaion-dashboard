import requests
import re

movie_id = 19995  # Avatar
url = f"https://www.themoviedb.org/movie/{movie_id}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

try:
    print(f"Fetching {url}...")
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Headers: {dict(r.headers)}")
    
    html = r.text
    # Search for og:image
    match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
    if match:
        print("Found matches:")
        print(match.group(1))
    else:
        print("No match 1 found.")
        match2 = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
        if match2:
            print("Found match 2:")
            print(match2.group(1))
        else:
            print("No match 2 found.")
            
    # Check if there is a meta image tag of any form
    meta_images = re.findall(r'<meta[^>]*content=["\']([^"\']+\.jpg[^"\']*)["\']', html)
    print("All found .jpg meta content:", meta_images[:5])
    
except Exception as e:
    print(f"Error occurred: {e}")
