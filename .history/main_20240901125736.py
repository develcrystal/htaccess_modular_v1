import threading
from tkinter import Tk
import os
import subprocess
from modules.gui import HTAccessOptimizerGUI
from modules.scraper import scrape_urls
from modules.file_handler import select_file, load_excel_urls, check_file_exists, parse_sitemap, save_results_and_report

# Global variables
output_dir = "output"  # Standard output directory

def start_processing_thread():
    use_threads = gui.get_threading_preference()
    htaccess_path = select_file('.htaccess') if gui.htaccess_var.get() else None
    excel_path = select_file('Coverage Drilldown Excel') if gui.excel_var.get() else None
    sitemap_url = gui.ask_for_sitemap_url() if gui.sitemap_var.get() else None
    base_url = gui.ask_for_base_url()

    if not base_url:
        gui.show_error_message("Fehler", "Keine Basis-URL angegeben. Skript wird abgebrochen.")
        return

    if (htaccess_path and not check_file_exists(htaccess_path, '.htaccess')) or \
       (excel_path and not check_file_exists(excel_path, 'Coverage Drilldown Excel')):
        return

    # Set output directory based on the current working directory
    output_dir = os.path.join(os.getcwd(), "output")
    
    # Start processing in a new thread
    threading.Thread(target=start_process, args=(use_threads, htaccess_path, excel_path, sitemap_url, base_url)).start()

def start_process(use_threads, htaccess_path, excel_path, sitemap_url, base_url):
    gui.set_status("Processing...")
    gui.update_progress(0)

    urls_to_test = []
    url_sources = []

    htaccess_results = {}
    excel_results = {}
    sitemap_results = {}

    # Process .htaccess file
    if htaccess_path:
        gui.set_status("Reading .htaccess file...")
        with open(htaccess_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith("Redirect"):
                parts = line.split()
                if len(parts) >= 3:
                    source_url = urljoin(base_url, parts[1])
                    destination_url = parts[2]
                    urls_to_test.append(source_url)
                    url_sources.append('htaccess')

    # Process Excel file
    if excel_path:
        gui.set_status("Loading URLs from Excel...")
        df = load_excel_urls(excel_path)
        for url in df['URL']:
            full_url = urljoin(base_url, url)
            urls_to_test.append(full_url)
            url_sources.append('Excel')

    # Process Sitemap
    if sitemap_url:
        gui.set_status("Parsing Sitemap...")
        sitemap_urls = parse_sitemap(sitemap_url)
        for url in sitemap_urls:
            full_url = urljoin(base_url, url)
            urls_to_test.append(full_url)
            url_sources.append('Sitemap')

    total_urls = len(urls_to_test)
    gui.set_status(f"Testing {total_urls} URLs...")

    for i, url in enumerate(urls_to_test):
        result, final_url = scrape_urls([url], use_threads)[0]
        source = url_sources[i]
        if source == 'htaccess':
            htaccess_results[url] = result
        elif source == 'Excel':
            excel_results[url] = result
        elif source == 'Sitemap':
            sitemap_results[url] = result
        
        gui.update_log_output(f"URL: {url} -> {final_url} (Source: {source}) - {result}", "success" if result == 'OK' else "error")
        progress = (i + 1) / total_urls * 100
        gui.update_progress(progress)

    gui.set_status("Saving results...")
    save_results_and_report(output_dir, htaccess_results, excel_results, sitemap_results)
    gui.set_status("Processing completed.")

def stop_process():
    # Handle stop process logic
    pass

def pause_process():
    # Handle pause process logic
    pass

def toggle_debug_mode():
    # Handle debug mode toggle
    pass

# GUI Setup
root = Tk()
gui = HTAccessOptimizerGUI(root, start_processing_thread, stop_process, pause_process, toggle_debug_mode)
root.mainloop()
