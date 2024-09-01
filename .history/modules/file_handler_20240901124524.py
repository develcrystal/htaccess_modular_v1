import os
import pandas as pd
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import requests

def select_file(file_type):
    # Diese Funktion sollte eine Datei auswählen (z.B. über einen Dateidialog).
    # Placeholder für den eigentlichen Dialog zum Dateiauswählen
    if file_type == '.htaccess':
        return "path/to/your/.htaccess"  # Hier sollte ein echter Dateipfad zurückgegeben werden
    elif file_type == 'Coverage Drilldown Excel':
        return "path/to/your/excel.xlsx"  # Hier sollte ein echter Dateipfad zurückgegeben werden

def load_excel_urls(excel_path):
    # Diese Funktion lädt URLs aus einer Excel-Datei.
    df = pd.read_excel(excel_path)
    return df

def check_file_exists(file_path, file_type):
    if not os.path.isfile(file_path):
        print(f"Fehler: {file_type} Datei '{file_path}' wurde nicht gefunden.")
        return False
    return True

def parse_sitemap(sitemap_url):
    # Diese Funktion parst eine Sitemap-URL und gibt eine Liste von URLs zurück.
    try:
        response = requests.get(sitemap_url)
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        urls = []
        for url in root.findall("ns:url/ns:loc", namespaces=namespace):
            urls.append(url.text)
        return urls
    except Exception as e:
        print(f"Fehler beim Parsen der Sitemap: {e}")
        return []
