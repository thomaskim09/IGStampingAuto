# IGStampingAuto/main.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
import socket
import time
from selenium import webdriver
from PIL import ImageTk

# Local module imports
import database
from automation import StampsAutomation
from ui_company_tab import CompanyTab
from ui_insurance_tab import InsuranceTab
from ui_automation_tab import AutomationTab
from ui_advanced_tab import AdvancedTab


# --- Helper function to find data files ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class IGStampingAuto(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IG Stamping Automation")

        try:
            icon_path = resource_path(os.path.join("resource", "app_icon.png"))
            if os.path.exists(icon_path):
                photo = ImageTk.PhotoImage(file=icon_path)
                self.iconphoto(False, photo)
        except Exception as e:
            print(f"Error setting application icon: {e}")

        window_width = 800
        window_height = 760
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # --- Core Application State Variables ---
        self.driver = None
        self.automation_instance = None
        self.adjudikasi_id = tk.StringVar()
        self.policy_number = tk.StringVar()
        self.output_dir_path = os.path.join(os.getcwd(), "output_stamped")
        self.uploaded_pdf_path = None
        self.all_company_names = []
        self.all_insurance_names = []
        self.stop_event = threading.Event()
        self.log_callback = None
        self.chrome_executable_path = ""

        # --- Tkinter UI Variables ---
        self.company_search_var = tk.StringVar()
        self.company_name = tk.StringVar()
        self.company_old_roc = tk.StringVar()
        self.company_new_roc = tk.StringVar()
        self.company_phone = tk.StringVar()
        self.company_address1 = tk.StringVar()
        self.company_address2 = tk.StringVar()
        self.company_address3 = tk.StringVar()
        self.company_city = tk.StringVar()
        self.company_postcode = tk.StringVar()
        self.company_state = tk.StringVar()
        self.source_pdf_var = tk.StringVar()
        self.export_dir_var = tk.StringVar()
        self.insurance_search_var = tk.StringVar()
        self.insurance_name = tk.StringVar()
        self.insurance_old_roc = tk.StringVar()
        self.insurance_new_roc = tk.StringVar()
        self.insurance_phone = tk.StringVar()
        self.insurance_address1 = tk.StringVar()
        self.insurance_address2 = tk.StringVar()
        self.insurance_address3 = tk.StringVar()
        self.insurance_city = tk.StringVar()
        self.insurance_postcode = tk.StringVar()
        self.insurance_state = tk.StringVar()

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Success.TButton",
            background="#d4edda",
            foreground="#155724",
            bordercolor="#c3e6cb",
        )
        style.configure(
            "Danger.TButton",
            background="#f8d7da",
            foreground="#721c24",
            bordercolor="#f5c6cb",
        )

        database.create_tables()
        if database.is_company_table_empty():
            database.preload_initial_companies()
        if database.is_insurance_table_empty():
            database.preload_initial_insurance()

        self.create_main_widgets()
        self.log_callback = self.automation_tab_ui.log_message
        self.load_company_names_to_search()
        self.load_insurance_names_to_search()
        self.auto_populate_default_insurance()
        self.attempt_reconnect_to_chrome()

    def update_status(self, text, color):
        status_frame = self.status_label.master
        status_frame.config(bg=color)
        self.status_label.config(background=color, foreground="white")
        self.status_var.set(text)

    def _threaded_chrome_check(self, is_retrying=False):
        if is_retrying:
            time.sleep(2)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", 9222))
        sock.close()

        if result == 0:
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_experimental_option(
                    "debuggerAddress", "127.0.0.1:9222"
                )
                driver = webdriver.Chrome(options=chrome_options)
                _ = driver.window_handles
                self.driver = driver
                self.automation_instance = StampsAutomation(
                    self.driver, self.stop_event, self.log_callback
                )
                self.after(0, self.update_status, "● Connected to Chrome", "#28a745")
            except Exception:
                self.driver = None
                self.automation_instance = None
                self.after(
                    0,
                    self.update_status,
                    "● Connection Error. Please 'Prepare Chrome'.",
                    "#ffc107",
                )
        else:
            self.driver = None
            self.automation_instance = None
            if not is_retrying:
                self.after(
                    0,
                    self.update_status,
                    "● Disconnected. Use 'Prepare Chrome' to start.",
                    "#6c757d",
                )

    def attempt_reconnect_to_chrome(self, is_retrying=False):
        if not is_retrying:
            self.update_status("Checking for Chrome...", "#ffc107")
        thread = threading.Thread(
            target=self._threaded_chrome_check, args=(is_retrying,), daemon=True
        )
        thread.start()

    def create_main_widgets(self):
        """Creates the main notebook, tabs, and status bar."""
        self.status_var = tk.StringVar()
        status_frame = tk.Frame(self, bg="#6c757d")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            padding=(10, 5),
            anchor=tk.W,
            font=("Segoe UI", 9, "bold"),
            background="#6c757d",
            foreground="white",
        )
        self.status_label.pack(fill=tk.X)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        company_tab_frame = ttk.Frame(self.notebook)
        insurance_tab_frame = ttk.Frame(self.notebook)
        automation_tab_frame = ttk.Frame(self.notebook)
        advanced_tab_frame = ttk.Frame(self.notebook)

        self.notebook.add(company_tab_frame, text="Company Information")
        self.notebook.add(insurance_tab_frame, text="Insurance Company Information")
        self.notebook.add(automation_tab_frame, text="Automation Steps")
        self.notebook.add(advanced_tab_frame, text="Advanced")

        self.company_tab_ui = CompanyTab(company_tab_frame, self)
        self.insurance_tab_ui = InsuranceTab(insurance_tab_frame, self)
        self.automation_tab_ui = AutomationTab(automation_tab_frame, self)
        self.advanced_tab_ui = AdvancedTab(advanced_tab_frame, self)

    def start_full_automation(self):
        self.stop_event.clear()
        if hasattr(self, "automation_tab_ui") and self.automation_tab_ui:
            threading.Thread(
                target=self.automation_tab_ui._threaded_full_automation, daemon=True
            ).start()
        else:
            messagebox.showerror("Error", "Automation components are not ready.")

    def stop_automation(self):
        if messagebox.askyesno(
            "Stop Automation",
            "Are you sure you want to stop the current automation process?",
        ):
            self.stop_event.set()
            self.update_status("Stopping automation...", "#ffc107")
            if self.log_callback:
                self.log_callback("User requested to stop automation.")
            self.update_status(
                "● Automation stop signal sent. Chrome remains open.", "#6c757d"
            )

    def load_company_names_to_search(self):
        self.all_company_names = database.get_all_company_names()
        if hasattr(self, "company_tab_ui") and self.company_tab_ui.company_combo:
            self.company_tab_ui.company_combo["values"] = self.all_company_names

    def load_insurance_names_to_search(self):
        self.all_insurance_names = database.get_all_insurance_company_names()
        if hasattr(self, "insurance_tab_ui") and self.insurance_tab_ui.insurance_combo:
            self.insurance_tab_ui.insurance_combo["values"] = self.all_insurance_names

    def auto_populate_default_insurance(self):
        if hasattr(self, "insurance_tab_ui"):
            names = database.get_all_insurance_company_names()
            if names:
                self.insurance_search_var.set(names[0])
                self.insurance_tab_ui.populate_insurance_form()


if __name__ == "__main__":
    app = IGStampingAuto()
    app.mainloop()
