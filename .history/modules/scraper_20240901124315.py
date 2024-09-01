import requests
from requests.exceptions import RequestException

def scrape_urls(urls, use_threads=False):
    results = []

    for url in urls:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                results.append(("OK", response.url))
            elif 300 <= response.status_code < 400:
                results.append((f"Redirect ({response.status_code})", response.url))
            else:
                results.append((f"Fehler ({response.status_code})", url))
        except RequestException as e:
            results.append((f"Fehler (Exception: {e})", url))

    return results
