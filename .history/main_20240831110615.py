from tkinter import Tk, BooleanVar, Checkbutton, ttk, messagebox
import threading
from modules.gui import HTAccessOptimizerGUI
from modules.scraper import scrape_urls
from modules.file_handler import select_file, get_base_url, get_sitemap_url, load_excel_urls, check_file_exists, parse_sitemap
from modules.gui import HTAccessOptimizerGUI
from modules.scraper import scrape_urls
from modules.file_handler import select_file, load_excel_urls, check_file_exists, parse_sitemap
import os
import sys
import subprocess



# Global variables
paused = False
stopped = False
debug_mode = False
excel_path = ""
output_dir = ""

def start_process():
    global paused, stopped, excel_path, output_dir

    use_threads = gui.get_threading_preference()
    htaccess_path = select_file('.htaccess')
    excel_path = select_file('Coverage Drilldown Excel')
    sitemap_url = gui.ask_for_sitemap_url()
    base_url = gui.ask_for_base_url()

    if not base_url:
        gui.show_error_message("Fehler", "Keine Basis-URL angegeben. Skript wird abgebrochen.")
        return

    if not (check_file_exists(htaccess_path, '.htaccess') and check_file_exists(excel_path, 'Coverage Drilldown Excel')):
        return

    urls = load_excel_urls(excel_path)  # Beispiel-URLs aus Excel laden
    sitemap_urls = list(parse_sitemap(sitemap_url))  # URLs aus Sitemap

    urls_to_test = urls + sitemap_urls

    results = scrape_urls(urls_to_test, use_threads)
    for result in results:
        gui.update_log_output(result[1], "success" if result[0] == "OK" else "error")

    gui.enable_excel_button()
    gui.enable_open_folder_button()

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

def open_excel_report():
    if os.name == "nt":
        os.startfile(excel_path)
    elif os.name == "posix":
        subprocess.Popen(["open", excel_path])

def open_output_folder():
    if os.name == "nt":
        os.startfile(output_dir)
    elif os.name == "posix":
        subprocess.Popen(["open", output_dir])

def restart_program():
    python = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    subprocess.Popen([python, script_path] + sys.argv[1:])
    sys.exit()

# GUI Setup
root = Tk()
gui = HTAccessOptimizerGUI(root, start_process, stop_process, pause_process, toggle_debug_mode)

# Set functions to the GUI buttons
gui.open_excel_report = open_excel_report
gui.open_output_folder = open_output_folder
gui.restart_program = restart_program

root.mainloop()
