from tkinter import Tk, BooleanVar, Checkbutton, ttk, messagebox
from modules.scraper import scrape_urls
from modules.file_handler import select_file, get_base_url, get_sitemap_url, load_excel_urls, check_file_exists

def start_process():
    use_threads = thread_var.get()

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

root = Tk()
root.title("Scraper GUI")

thread_var = BooleanVar()
thread_checkbox = Checkbutton(root, text="Threading verwenden", variable=thread_var)
thread_checkbox.pack(anchor='w')

start_button = ttk.Button(root, text="Start", command=start_process)
start_button.pack(side="left", padx=10, pady=20)

root.mainloop()
