import threading
import time
from modules.ssl_handler import request_with_ssl
imp

def scrape_url(url):
    try:
        response = request_with_ssl(url)
        response.raise_for_status()
        return "OK", url
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", url

def scrape_with_threads(urls):
    results = []
    threads = []
    for url in urls:
        thread = threading.Thread(target=lambda: results.append(scrape_url(url)))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Prevent too many requests at once

    for thread in threads:
        thread.join()

    return results

def scrape_urls(urls, use_threads=False):
    if use_threads:
        return scrape_with_threads(urls)
    else:
        return [scrape_url(url) for url in urls]
