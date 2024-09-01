from tkinter import Tk, BooleanVar, Checkbutton, ttk, Text, Scrollbar, VERTICAL, RIGHT, Y, END
from tkinter import font

class HTAccessOptimizerGUI:
    def __init__(self, root, start_process_callback, stop_process_callback, pause_process_callback, toggle_debug_mode_callback):
        self.root = root
        self.root.title("HTAccess Optimizer GUI")
        self.root.geometry("600x600")

        self.status_label = ttk.Label(root, text="Bereit zur Verarbeitung...", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.log_frame = ttk.Frame(root)
        self.log_frame.pack(pady=10, fill="both", expand=True)
        self.scrollbar = Scrollbar(self.log_frame, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.log_font = font.Font(family="Helvetica", size=8)
        self.log_output = Text(self.log_frame, height=10, yscrollcommand=self.scrollbar.set, font=self.log_font)
        self.log_output.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.log_output.yview)

        self.log_output.tag_config("success", foreground="green", background="white")
        self.log_output.tag_config("redirect", foreground="darkorange", background="yellow")
        self.log_output.tag_config("error", foreground="red", background="lightcoral")

        self.htaccess_var = BooleanVar()
        self.excel_var = BooleanVar()
        self.sitemap_var = BooleanVar()

        self.htaccess_checkbox = Checkbutton(root, text="htaccess verwenden", variable=self.htaccess_var)
        self.htaccess_checkbox.pack(anchor='w')
        self.excel_checkbox = Checkbutton(root, text="GSC Coverage-Drilldown-Excel verwenden", variable=self.excel_var)
        self.excel_checkbox.pack(anchor='w')
        self.sitemap_checkbox = Checkbutton(root, text="Sitemap verwenden", variable=self.sitemap_var)
        self.sitemap_checkbox.pack(anchor='w')

        self.start_button = ttk.Button(root, text="Start", command=start_process_callback)
        self.start_button.pack(side="left", padx=10, pady=20)

        self.stop_button = ttk.Button(root, text="Abbrechen", command=stop_process_callback)
        self.stop_button.pack(side="left", padx=10, pady=20)

        self.pause_button = ttk.Button(root, text="Pause", command=pause_process_callback)
        self.pause_button.pack(side="left", padx=10, pady=20)

        self.debug_checkbox = Checkbutton(root, text="Debug-Modus", variable=BooleanVar(), command=toggle_debug_mode_callback)
        self.debug_checkbox.pack(side="left", padx=10, pady=20)

    def update_log_output(self, message, tag):
        self.log_output.insert(END, message + "\n", tag)
        self.log_output.yview(END)

    def set_status(self, text):
        self.status_label.config(text=text)

    def update_progress(self, value):
        self.progress_bar["value"] = value
        self.root.update_idletasks()

    def get_threading_preference(self):
        return self.htaccess_var.get()

    def get_excel_preference(self):
        return self.excel_var.get()

    def get_sitemap_preference(self):
        return self.sitemap_var.get()
