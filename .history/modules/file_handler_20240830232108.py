import re
from urllib.parse import urljoin
import pandas as pd

def replace_placeholders_with_domain(urls, base_url):
    updated_urls = []
    for url in urls:
        if re.search(r'\(\.\*\)', url):
            url = re.sub(r'\(\.\*\)', '', url)
        if not url.startswith(base_url):
            url = urljoin(base_url, url)
        updated_urls.append(url)
    return updated_urls

def load_excel_urls(excel_path):
    df = pd.read_excel(excel_path, sheet_name=1)
    urls = df['URL'].dropna().tolist()
    return urls

# Weitere Funktionen zum Laden und Verarbeiten von .htaccess und Sitemaps können hier hinzugefügt werden.
