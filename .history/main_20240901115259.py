import os
import threading
import tkinter as tk
from tkinter import messagebox
from modules.file_handler import select_file, load_excel_urls, check_file_exists, parse_sitemap, save_results_and_report
from modules.scraper import scrape_urls  # Sicherstellen, dass dies importiert ist

# Globale Variablen
output_dir = ""
paused = False
stopped = False

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

        self.progress_bar = tk.DoubleVar()
        self.progress = tk.Progressbar(self.master, variable=self.progress_bar, maximum=100)
        self.progress.pack()

    def set_status(self, message: str) -> None:
        self.status_label.config(text=f"Status: {message}")

    def update_progress(self, value: float) -> None:
        self.progress_bar.set(value)

    def start_processing_thread(self) -> None:
        global output_dir
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
        
        processing_thread = threading.Thread(target=self.start_process, args=(htaccess_path, excel_path, sitemap_url, base_url))
        processing_thread.start()

    def start_process(self, htaccess_path, excel_path, sitemap_url, base_url) -> None:
        global paused, stopped

        self.set_status("Verarbeitung läuft...")
        self.update_progress(0)
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        urls_to_test = []
        url_sources = []

        # HTACCESS verarbeiten
        if htaccess_path:
            self.set_status("Lese .htaccess-Datei ein...")
            with open(htaccess_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for line in lines:
                if line.startswith("Redirect"):
                    parts = line.split()
                    if len(parts) >= 3:
                        source_url = parts[1]
                        urls_to_test.append(source_url)
                        url_sources.append('htaccess')

        # Excel-Datei verarbeiten
        if excel_path:
            self.set_status("Lade URLs aus der Excel-Datei...")
            df = load_excel_urls(excel_path)
            for url in df['URL']:
                urls_to_test.append(url)
                url_sources.append('Excel')

        # Sitemap-URLs verarbeiten
        if sitemap_url:
            self.set_status("Parsen der Sitemap...")
            sitemap_urls = list(parse_sitemap(sitemap_url))
            urls_to_test.extend(sitemap_urls)
            url_sources.extend(['Sitemap'] * len(sitemap_urls))

        total_urls = len(urls_to_test)
        self.set_status(f"Teste {total_urls} URLs...")

        for i, url in enumerate(urls_to_test):
            while paused:
                pass
            
            if stopped:
                self.set_status("Verarbeitung gestoppt.")
                break

            result, final_url = scrape_urls([url])[0]
            source = url_sources[i]

            # Ergebnis verarbeiten (z.B. speichern oder loggen)

            progress = (i + 1) / total_urls * 100
            self.update_progress(progress)

        self.set_status("Verarbeitung abgeschlossen.")
        self.reset_gui_state()

    def pause_processing(self) -> None:
        global paused
        paused = True
        self.set_status("Verarbeitung pausiert.")

    def stop_processing(self) -> None:
        global stopped
        stopped = True
        self.set_status("Verarbeitung gestoppt.")

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