import re
import os
import pandas as pd
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from tkinter import filedialog, simpledialog
import requests

def select_file(file_type):
    file_path = filedialog.askopenfilename(title=f"Wähle die {file_type} Datei aus")
    return file_path

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
    urls = df.iloc[:, 0].dropna().tolist()
    return urls

def parse_sitemap(sitemap_url):
    sitemap_urls = set()
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        if root.tag.endswith('sitemapindex'):
            for sitemap in root.findall('ns:sitemap/ns:loc', namespace):
                child_sitemap_url = sitemap.text.strip()
                sitemap_urls.update(parse_sitemap(child_sitemap_url))
        elif root.tag.endswith('urlset'):
            for url in root.findall('ns:url/ns:loc', namespace):
                sitemap_urls.add(url.text.strip())

    except Exception as e:
        print(f"Fehler beim Einlesen der Sitemap {sitemap_url}: {str(e)}")
    
    return sitemap_urls

def get_base_url():
    base_url = simpledialog.askstring("Stamm-URL", "Bitte geben Sie die Stamm-URL Ihrer Website ein (z.B. https://www.contify.de):")
    return base_url

def get_sitemap_url():
    sitemap_url = simpledialog.askstring("Sitemap-URL", "Bitte geben Sie die URL Ihrer Sitemap ein (z.B. https://www.contify.de/sitemap.xml):")
    return sitemap_url

def check_file_exists(file_path, file_type):
    if not os.path.exists(file_path):
        print(f"Die {file_type}-Datei wurde nicht gefunden. Bitte überprüfen.")
        return False
    return True
