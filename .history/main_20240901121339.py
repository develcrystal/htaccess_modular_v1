import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from modules.file_handler import select_file, load_excel_urls, check_file_exists, parse_sitemap, save_results_and_report
from modules.scraper import scrape_urls
from modules.log_handler import LogHandler

# Global Variables
output_dir = ""
paused = False
stopped = False
process_thread = None  # Manage thread globally

class HTAccessOptimizerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("HTAccess Optimizer")
        self.create_widgets()

    def create_widgets(self):
        self.start_button = tk.Button(self.master, text="Start", command=self.start_processing_thread)
        self.start_button.pack()

        self.pause_button = tk.Button(self.master, text="Pause", command=self.pause_processing)
        self.pause_button.pack()
        self.pause_button.config(state="disabled")

        self.stop_button = tk.Button(self.master, text="Stop", command=self.stop_processing)
        self.stop_button.pack()
        self.stop_button.config(state="disabled")

        self.status_label = tk.Label(self.master, text="Status: Bereit")
        self.status_label.pack()

        self.progress_bar = ttk.Progressbar(self.master, maximum=100)
        self.progress_bar.pack()

        # Initialize LogHandler
        self.log_output = tk.Text(self.master)
        self.log_output.pack(fill="both", expand=True)
        self.log_handler = LogHandler(self.log_output)

    def set_status(self, message: str) -> None:
        self.status_label.config(text=f"Status: {message}")

    def update_progress(self, value: float) -> None:
        self.progress_bar['value'] = value

    def start_processing_thread(self) -> None:
        global output_dir, process_thread

        if process_thread and process_thread.is_alive():
            messagebox.showwarning("Warnung", "Ein Prozess läuft bereits. Bitte stoppen Sie ihn zuerst.")
            return

        htaccess_path = select_file('.htaccess')
        excel_path = select_file('Coverage Drilldown Excel')
        sitemap_url = self.ask_for_sitemap_url()
        base_url = self.ask_for_base_url()

        if not base_url:
            self.show_error_message("Fehler", "Keine Basis-URL angegeben. Skript wird abgebrochen.")
            return

        if (htaccess_path and not check_file_exists(htaccess_path, '.htaccess')) or \
           (excel_path and not check_file_exists(excel_path, 'Coverage Drilldown Excel')):
            return

        output_dir = os.path.join(os.getcwd(), "output")

        process_thread = threading.Thread(target=self.start_process, args=(htaccess_path, excel_path, sitemap_url, base_url))
        process_thread.start()

    def start_process(self, htaccess_path, excel_path, sitemap_url, base_url) -> None:
        global paused, stopped

        self.set_status("Verarbeitung läuft...")
        self.update_progress(0)
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        urls_to_test = []
        url_sources = []

        # Process HTACCESS
        if htaccess_path:
            self.log_handler.log_info("Lese .htaccess-Datei ein...")
            with open(htaccess_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for line in lines:
                if line.startswith("Redirect"):
                    parts = line.split()
                    if len(parts) >= 3:
                        source_url = parts[1]
                        urls_to_test.append(source_url)
                        url_sources.append('htaccess')

        # Process Excel File
        if excel_path:
            self.log_handler.log_info("Lade URLs aus der Excel-Datei...")
            df = load_excel_urls(excel_path)
            for url in df['URL']:
                urls_to_test.append(url)
                url_sources.append('Excel')

        # Process Sitemap URLs
        if sitemap_url:
            self.log_handler.log_info("Parsen der Sitemap...")
            sitemap_urls = list(parse_sitemap(sitemap_url))
            urls_to_test.extend(sitemap_urls)
            url_sources.extend(['Sitemap'] * len(sitemap_urls))

        total_urls = len(urls_to_test)
        self.set_status(f"Teste {total_urls} URLs...")

        for i, url in enumerate(urls_to_test):
            while paused:
                self.set_status("Verarbeitung pausiert.")
                self.master.update()

            if stopped:
                self.set_status("Verarbeitung gestoppt.")
                break

            result, final_url = scrape_urls([url])[0]
            source = url_sources[i]

            # Process result (e.g., save or log)
            if "OK" in result:
                self.log_handler.log_success(f"Teste URL {i+1} von {total_urls}: {url} (Quelle: {source}) - OK")
            elif "Redirect" in result:
                self.log_handler.log_redirect(f"Teste URL {i+1} von {total_urls}: {url} (Quelle: {source}) - Redirect")
            else:
                self.log_handler.log_error(f"Teste URL {i+1} von {total_urls}: {url} (Quelle: {source}) - Error")

            progress = (i + 1) / total_urls * 100
            self.update_progress(progress)

        self.set_status("Verarbeitung abgeschlossen.")
        self.reset_gui_state()

    def pause_processing(self) -> None:
        global paused
        paused = not paused
        if paused:
            self.pause_button.config(text="Fortsetzen")
        else:
            self.pause_button.config(text="Pause")

    def stop_processing(self) -> None:
        global stopped
        stopped = True
        self.set_status("Verarbeitung wird gestoppt...")

    def show_error_message(self, title: str, message: str) -> None:
        messagebox.showerror(title, message)

    def reset_gui_state(self) -> None:
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.update_progress(0)

def main() -> None:
    root = tk.Tk()
    app = HTAccessOptimizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
