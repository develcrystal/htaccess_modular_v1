import threading
import time
from modules.ssl_handler import request_with_ssl
import requests

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

def scrape_urls(urls, use_threads):
    # Dummy-Implementierung zum Scrapen von URLs
    results = []
    for url in urls:
        # Simuliere das Scrapen
        result = "OK"  # oder "Redirect", "Error" usw.
        final_url = url  # Hier sollte die endgültige URL stehen
        results.append((result, final_url))
    return results
