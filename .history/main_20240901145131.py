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
        self.master.title("HTAccess Optimizer GUI")
        self.master.geometry("800x600")  # Set window size to match the older version
        self.create_widgets()

    def create_widgets(self):
        # Status Label
        self.status_label = ttk.Label(self.master, text="Bereit zur Verarbeitung...", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=700, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Log Output Frame
        self.log_frame = ttk.Frame(self.master)
        self.log_frame.pack(pady=10, fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.log_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_output = tk.Text(self.log_frame, height=10, yscrollcommand=self.scrollbar.set, font=("Helvetica", 10))
        self.log_output.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.log_output.yview)

        # Initialize LogHandler
        self.log_handler = LogHandler(self.log_output)

        # Checkboxes for Options
        self.htaccess_var = tk.BooleanVar()
        self.excel_var = tk.BooleanVar()
        self.sitemap_var = tk.BooleanVar()

        self.htaccess_checkbox = tk.Checkbutton(self.master, text="htaccess verwenden", variable=self.htaccess_var)
        self.htaccess_checkbox.pack(anchor='w')
        self.excel_checkbox = tk.Checkbutton(self.master, text="GSC Coverage-Drilldown-Excel verwenden", variable=self.excel_var)
        self.excel_checkbox.pack(anchor='w')
        self.sitemap_checkbox = tk.Checkbutton(self.master, text="Sitemap verwenden", variable=self.sitemap_var)
        self.sitemap_checkbox.pack(anchor='w')

        # Buttons for Actions
        self.start_button = ttk.Button(self.master, text="Start", command=self.start_processing_thread)
        self.start_button.pack(side="left", padx=10, pady=20)

        self.pause_button = ttk.Button(self.master, text="Pause", command=self.pause_processing)
        self.pause_button.pack(side="left", padx=10, pady=20)
        self.pause_button.config(state="disabled")

        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_processing)
        self.stop_button.pack(side="left", padx=10, pady=20)
        self.stop_button.config(state="disabled")

        self.debug_checkbox = tk.Checkbutton(self.master, text="Debug-Modus", variable=tk.BooleanVar(), command=self.toggle_debug_mode)
        self.debug_checkbox.pack(side="left", padx=10, pady=20)

        # Additional GUI Elements
        self.excel_button = ttk.Button(self.master, text="Ergebnis-Excel öffnen", command=self.open_excel_report, state="disabled")
        self.excel_button.pack(side="left", padx=10, pady=20)

        self.restart_button = ttk.Button(self.master, text="Neustart", command=self.restart_program)
        self.restart_button.pack(side="left", padx=10, pady=20)

        self.exit_button = ttk.Button(self.master, text="Beenden", command=self.exit_program)
        self.exit_button.pack(side="left", padx=10, pady=20)

        self.open_folder_button = ttk.Button(self.master, text="Ergebnisordner öffnen", state="disabled", command=self.open_output_folder)
        self.open_folder_button.pack(side="left", padx=10, pady=20)

    def set_status(self, message: str) -> None:
        self.status_label.config(text=message)

    def update_progress(self, value: float) -> None:
        self.progress_bar['value'] = value
        self.master.update_idletasks()

    def start_processing_thread(self) -> None:
        global output_dir, process_thread

        if process_thread and process_thread.is_alive():
            messagebox.showwarning("Warnung", "Ein Prozess läuft bereits. Bitte stoppen Sie ih
