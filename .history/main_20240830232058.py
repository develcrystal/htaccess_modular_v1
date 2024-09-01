from tkinter import Tk, BooleanVar, Checkbutton, ttk, messagebox
from modules.scraper import scrape_urls
from modules.file_handler import load_excel_urls

def start_process():
    use_threads = thread_var.get()
    urls = ["https://example.com"]  # Beispiel-URLs
    results = scrape_urls(urls, use_threads)
    for result in results:
        print(result)

root = Tk()
root.title("Scraper GUI")

thread_var = BooleanVar()
thread_checkbox = Checkbutton(root, text="Threading verwenden", variable=thread_var)
thread_checkbox.pack(anchor='w')

start_button = ttk.Button(root, text="Start", command=start_process)
start_button.pack(side="left", padx=10, pady=20)

root.mainloop()
