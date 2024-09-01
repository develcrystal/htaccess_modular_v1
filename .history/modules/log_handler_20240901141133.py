import tkinter as tk
from tkinter import END

class LogHandler:
    def __init__(self, log_output: tk.Text):
        self.log_output = log_output
        self.setup_tags()

    def setup_tags(self):
        self.log_output.tag_config("success", foreground="green", background="white")
        self.log_output.tag_config("redirect", foreground="darkorange", background="yellow")
        self.log_output.tag_config("error", foreground="red", background="lightcoral")

    def insert_log(self, message: str, tag: str):
        self.log_output.insert(END, message + "\n", tag)
        self.log_output.yview(END)

    def log_success(self, message: str):
        self.insert_log(message, "success")

    def log_redirect(self, message: str):
        self.insert_log(message, "redirect")

    def log_error(self, message: str):
        self.insert_log(message, "error")

    def log_info(self, message: str):
        self.insert_log(message, None)
