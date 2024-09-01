from tkinter import Tk, BooleanVar, Checkbutton, ttk, messagebox
from modules.scraper import scrape_urls
from modules.file_handler import select_file, get_base_url, get_sitemap_url, load_excel_urls, check_file_exists, parse_sitemap
import threading
from modules.gui import HTAccessOptimizerGUI



# Global variables
paused = False
stopped = False
debug_mode = False  # Hier die Variable hinzufügen

def start_process():
    use_threads = gui.get_threading_preference()

    htaccess_path = select_file('.htaccess')
    excel_path = select_file('Coverage Drilldown Excel')
    sitemap_url = get_sitemap_url()
    base_url = get_base_url()

    if not base_url:
        print("Keine Stamm-URL angegeben. Skript wird abgebrochen.")
        return

    if not (check_file_exists(htaccess_path, '.htaccess') and check_file_exists(excel_path, 'Coverage Drilldown Excel')):
        return

    urls = load_excel_urls(excel_path)  # Beispiel-URLs aus Excel laden
    sitemap_urls = list(parse_sitemap(sitemap_url))  # URLs aus Sitemap

    urls_to_test = urls + sitemap_urls

    results = scrape_urls(urls_to_test, use_threads)
    for result in results:
        print(result)

def stop_process():
    global stopped
    stopped = True
    gui.update_log_output("Verarbeitung wird abgebrochen...\n", "error")

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

# GUI Setup
root = Tk()
gui = HTAccessOptimizerGUI(root, start_process, stop_process, pause_process, toggle_debug_mode)
root.mainloop()
