import threading
from modules.gui import HTAccessOptimizerGUI
from modules.scraper import scrape_urls
from modules.file_handler import select_file, load_excel_urls, check_file_exists, parse_sitemap
import os
import sys
import subprocess
from tkinter import Tk, BooleanVar, Checkbutton, ttk, messagebox

