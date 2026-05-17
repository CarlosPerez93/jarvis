import urllib.request
import urllib.parse
import re

def get_first_youtube_result(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            # Let's search for watch?v= matches
            matches = re.findall(r'/watch\?v=[a-zA-Z0-9_-]{11}', html)
            if matches:
                # Deduplicate and return the first one
                # Usually the first few matches might be identical or playlist/ads, 
                # but /watch?v=XXXXXXXXXXX is the standard video pattern.
                unique_matches = []
                for m in matches:
                    if m not in unique_matches:
                        unique_matches.append(m)
                print("Found matches:", unique_matches[:5])
                return "https://www.youtube.com" + unique_matches[0]
            else:
                print("No matches found in HTML")
                return None
    except Exception as e:
        print("Error fetching page:", e)
        return None

if __name__ == "__main__":
    url = get_first_youtube_result("ya te olvide")
    print("First video URL:", url)
