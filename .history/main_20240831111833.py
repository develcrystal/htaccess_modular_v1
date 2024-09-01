import threading
from tkinter import Tk
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
output_dir = ""

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

    # Start the processing thread with the user input already gathered
    processing_thread = threading.Thread(target=start_process, args=(use_threads, htaccess_path, excel_path, sitemap_url, base_url))
    processing_thread.start()

def start_process(use_threads, htaccess_path, excel_path, sitemap_url, base_url):
    global paused, stopped, output_dir

    # Verhindern, dass der Benutzer während der Verarbeitung interagiert
    gui.set_status("Verarbeitung läuft...")
    gui.start_button.config(state="disabled")
    gui.pause_button.config(state="normal")
    gui.stop_button.config(state="normal")

    urls_to_test = []
    invalid_urls = []
    error_logs = []
    url_sources = []

    htaccess_results = {}
    excel_results = {}
    sitemap_results = []

    if htaccess_path:
        with open(htaccess_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # (Processing logic here)

    if excel_path:
        df = pd.read_excel(excel_path, sheet_name=1)
        # (Processing logic here)

    if sitemap_url:
        sitemap_urls = list(parse_sitemap(sitemap_url))  # URLs aus Sitemap
        urls_to_test.extend(sitemap_urls)

    # (Test each URL logic here)
    # Assuming that you have already implemented the URL testing logic

    gui.enable_excel_button()
    gui.enable_open_folder_button()

    save_results_and_report(output_dir, htaccess_results, excel_results, sitemap_results)

    # Zurücksetzen der GUI, nachdem die Verarbeitung abgeschlossen ist
    reset_gui_state()

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
    python = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    subprocess.Popen([python, script_path] + sys.argv[1:])
    sys.exit()

def reset_gui_state():
    gui.set_status("Bereit zur Verarbeitung...")
    gui.start_button.config(state="normal")
    gui.pause_button.config(state="disabled")
    gui.stop_button.config(state="disabled")

# GUI Setup
root = Tk()
gui = HTAccessOptimizerGUI(root, start_processing_thread, stop_process, pause_process, toggle_debug_mode)

# Set functions to the GUI buttons
gui.open_excel_report = open_excel_report
gui.open_output_folder = open_output_folder
gui.restart_program = restart_program

root.mainloop()
