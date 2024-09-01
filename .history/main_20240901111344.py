import threading
from tkinter import Tk, END
from modules.gui import HTAccessOptimizerGUI
from modules.scraper import scrape_urls
from modules.file_handler import select_file, load_excel_urls, check_file_exists, parse_sitemap, save_results_and_report
import os
import sys
import subprocess

# Global variables
paused = False
stopped = False
debug_mode = False
output_dir = "output"  # Standard-Ausgabeverzeichnis festlegen

def start_process(use_threads, htaccess_path, excel_path, sitemap_url, base_url):
    global paused, stopped, output_dir

    # Setze den Status auf "Verarbeitung läuft..."
    gui.set_status("Verarbeitung läuft...")
    gui.update_progress(0)  # Setze den Fortschrittsbalken auf 0
    gui.start_button.config(state="disabled")
    gui.pause_button.config(state="normal")
    gui.stop_button.config(state="normal")

    urls_to_test = []
    url_sources = []

    htaccess_results = {}
    excel_results = {}
    sitemap_results = []

    # Verarbeitung der .htaccess-Datei
    if htaccess_path:
        gui.set_status("Lese .htaccess-Datei ein...")
        with open(htaccess_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith("Redirect"):
                parts = line.split()
                if len(parts) >= 3:
                    source_url = parts[1]
                    destination_url = parts[2]
                    urls_to_test.append(source_url)
                    url_sources.append('htaccess')

    # Verarbeitung der Excel-Datei
    if excel_path:
        gui.set_status("Lade URLs aus der Excel-Datei...")
        df = load_excel_urls(excel_path)
        for url in df['URL']:
            urls_to_test.append(url)
            url_sources.append('Excel')

    # Verarbeitung der Sitemap-URLs
    if sitemap_url:
        gui.set_status("Parsen der Sitemap...")
        sitemap_urls = list(parse_sitemap(sitemap_url))  # URLs aus der Sitemap extrahieren
        urls_to_test.extend(sitemap_urls)
        url_sources.extend(['Sitemap'] * len(sitemap_urls))

    total_urls = len(urls_to_test)
    gui.set_status(f"Teste {total_urls} URLs...")

    # Test each URL
    for i, url in enumerate(urls_to_test):
        result, final_url = scrape_urls([url], use_threads)[0]
        source = url_sources[i]
        if source == 'htaccess':
            htaccess_results[url] = result
        elif source == 'Excel':
            excel_results[url] = result
        elif source == 'Sitemap':
            sitemap_results.append({'url': url, 'status': result})
        
        # Log the result
        if result == 'OK':
            gui.update_log_output(f"URL: {url} -> {final_url} (Quelle: {source}) - {result}", "success")
        elif 'Redirect' in result:
            gui.update_log_output(f"URL: {url} -> {final_url} (Quelle: {source}) - {result}", "redirect")
        else:
            gui.update_log_output(f"URL: {url} -> {final_url} (Quelle: {source}) - {result}", "error")

        # Aktualisiere den Fortschrittsbalken
        progress = (i + 1) / total_urls * 100
        gui.update_progress(progress)

    gui.set_status("Speichern der Ergebnisse...")
    gui.enable_excel_button()
    gui.enable_open_folder_button()

    save_results_and_report(output_dir, htaccess_results, excel_results, sitemap_results)

    gui.set_status("Verarbeitung abgeschlossen.")
    # Zurücksetzen der GUI, nachdem die Verarbeitung abgeschlossen ist
    reset_gui_state()

def start_process(use_threads, htaccess_path, excel_path, sitemap_url, base_url):
    global paused, stopped, output_dir

    # Verhindern, dass der Benutzer während der Verarbeitung interagiert
    gui.set_status("Verarbeitung läuft...")
    gui.start_button.config(state="disabled")
    gui.pause_button.config(state="normal")
    gui.stop_button.config(state="normal")

    urls_to_test = []
    url_sources = []

    htaccess_results = {}
    excel_results = {}
    sitemap_results = []

    # Verarbeitung der .htaccess-Datei
    if htaccess_path:
        with open(htaccess_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith("Redirect"):
                parts = line.split()
                if len(parts) >= 3:
                    source_url = parts[1]
                    destination_url = parts[2]
                    urls_to_test.append(source_url)
                    url_sources.append('htaccess')

    # Verarbeitung der Excel-Datei
    if excel_path:
        df = load_excel_urls(excel_path)
        for url in df['URL']:
            urls_to_test.append(url)
            url_sources.append('Excel')

    # Verarbeitung der Sitemap-URLs
    if sitemap_url:
        sitemap_urls = list(parse_sitemap(sitemap_url))  # URLs aus der Sitemap extrahieren
        urls_to_test.extend(sitemap_urls)
        url_sources.extend(['Sitemap'] * len(sitemap_urls))

    # Test each URL
    for i, url in enumerate(urls_to_test):
        result, final_url = scrape_urls([url], use_threads)[0]
        source = url_sources[i]
        if source == 'htaccess':
            htaccess_results[url] = result
        elif source == 'Excel':
            excel_results[url] = result
        elif source == 'Sitemap':
            sitemap_results.append({'url': url, 'status': result})
        
        # Log the result
        if result == 'OK':
            gui.update_log_output(f"URL: {url} -> {final_url} (Quelle: {source}) - {result}", "success")
        elif 'Redirect' in result:
            gui.update_log_output(f"URL: {url} -> {final_url} (Quelle: {source}) - {result}", "redirect")
        else:
            gui.update_log_output(f"URL: {url} -> {final_url} (Quelle: {source}) - {result}", "error")

    gui.enable_excel_button()
    gui.enable_open_folder_button()

    save_results_and_report(output_dir, htaccess_results, excel_results, sitemap_results)

    # Zurücksetzen der GUI, nachdem die Verarbeitung abgeschlossen ist
    reset_gui_state()

def reset_gui_state():
    gui.set_status("Bereit zur Verarbeitung...")
    gui.start_button.config(state="normal")
    gui.pause_button.config(state="disabled")
    gui.stop_button.config(state="disabled")
    gui.log_output.delete(1.0, END)  # Löscht das Log-Ausgabefeld

def stop_process():
    global stopped
    stopped = True
    gui.update_log_output("Verarbeitung wird abgebrochen...\n", "error")
    reset_gui_state()

def pause_process():
    global paused
    paused = not paused
    if paused:
        gui.pause_button.config(text="Fortsetzen")
        gui.set_status("Verarbeitung pausiert.")
        gui.update_log_output("Verarbeitung pausiert...\n", "error")
    else:
        gui.pause_button.config(text="Pause")
        gui.set_status("Verarbeitung wird fortgesetzt.")
        gui.update_log_output("Verarbeitung wird fortgesetzt...\n", "error")

def toggle_debug_mode():
    global debug_mode
    debug_mode = not debug_mode
    gui.update_log_output(f"Debug-Modus {'aktiviert' if debug_mode else 'deaktiviert'}.\n", "success")

def open_excel_report():
    if os.name == "nt":
        os.startfile(output_dir)
    elif os.name == "posix":
        subprocess.Popen(["open", output_dir])

def open_output_folder():
    if os.name == "nt":
        os.startfile(output_dir)
    elif os.name == "posix":
        subprocess.Popen(["open", output_dir])

def restart_program():
    global stopped
    stopped = True  # Signal an alle laufenden Threads, sich zu beenden
    reset_gui_state()  # Setzt die GUI zurück

    # Schließen des aktuellen Fensters
    root.quit()
    root.destroy()

    # Neustart des Programms
    python = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    subprocess.Popen([python, script_path] + sys.argv[1:])
    sys.exit()

# GUI Setup
root = Tk()
gui = HTAccessOptimizerGUI(root, start_processing_thread, stop_process, pause_process, toggle_debug_mode)

# Set functions to the GUI buttons
gui.open_excel_report = open_excel_report
gui.open_output_folder = open_output_folder
gui.restart_program = restart_program

root.mainloop()
