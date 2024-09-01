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

def save_results_and_report(output_dir, htaccess_results, excel_results, sitemap_results):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Zusammenstellen der Ergebnisse
    all_results = []

    # htaccess results verarbeiten
    for url, result in htaccess_results.items():
        all_results.append({'URL': url, 'Source': 'htaccess', 'Result': result})

    # excel results verarbeiten
    for url, result in excel_results.items():
        all_results.append({'URL': url, 'Source': 'Excel', 'Result': result})

    # sitemap results verarbeiten
    for result in sitemap_results:
        all_results.append({'URL': result['url'], 'Source': 'Sitemap', 'Result': result['status']})

    # Umwandeln in DataFrame
    df = pd.DataFrame(all_results)

    # Speichern als Excel-Datei
    output_file = os.path.join(output_dir, "results.xlsx")
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Results')

    # Zugriff auf das Arbeitsblatt
    workbook = writer.book
    worksheet = writer.sheets['Results']

    # Farben anwenden basierend auf den Ergebnissen
    format_ok = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    format_redirect = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
    format_error = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

    for row_num, row_data in df.iterrows():
        if row_data['Result'] == 'OK':
            worksheet.write(row_num + 1, 2, row_data['Result'], format_ok)
        elif 'Redirect' in row_data['Result']:
            worksheet.write(row_num + 1, 2, row_data['Result'], format_redirect)
        else:
            worksheet.write(row_num + 1, 2, row_data['Result'], format_error)

    writer.save()

    print(f"Results saved to {output_file}")
