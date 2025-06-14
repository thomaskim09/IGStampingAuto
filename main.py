# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import socket
import time
from selenium import webdriver

# Local module imports
import database
from automation import StampsAutomation
from ui_company_tab import CompanyTab
from ui_insurance_tab import InsuranceTab
from ui_automation_tab import AutomationTab


class IGStampingAuto(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IG Stamping Automation")
        self.geometry("800x725")  # Increased height for the status bar

        # --- Core Application State Variables ---
        self.driver = None
        self.automation_instance = None
        self.adjudikasi_id = tk.StringVar()
        self.output_dir_path = os.path.join(os.getcwd(), "output_stamped")
        os.makedirs(self.output_dir_path, exist_ok=True)
        self.uploaded_pdf_path = None
        self.all_company_names = []
        self.all_insurance_names = []
        self.stop_event = threading.Event()  # Initialize the stop event
        self.log_callback = None  # Will be set by AutomationTab

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

        # --- Style Configuration ---
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

        # --- Database Setup ---
        database.create_tables()
        if database.is_company_table_empty():
            database.preload_initial_companies()
        if database.is_insurance_table_empty():
            database.preload_initial_insurance()

        # --- UI Initialization ---
        self.create_main_widgets()
        # Set the log_callback AFTER automation_tab_ui is initialized
        self.log_callback = self.automation_tab_ui.log_message
        self.load_company_names_to_search()
        self.load_insurance_names_to_search()
        self.auto_populate_default_insurance()

        # --- Start the non-blocking check on startup ---
        self.attempt_reconnect_to_chrome()

    def update_status(self, text, color):
        """Thread-safe method to update the status bar."""
        status_frame = self.status_label.master
        status_frame.config(bg=color)
        self.status_label.config(background=color, foreground="white")
        self.status_var.set(text)

    def _threaded_chrome_check(self, is_retrying=False):
        """
        Runs in a background thread. Uses a fast socket check and then
        connects with Selenium, updating the UI based on the result.
        """
        if is_retrying:
            time.sleep(2)  # Give Chrome a moment to start up after launch

        # Fast check using a socket to see if the port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Short timeout of 1 second
        result = sock.connect_ex(("127.0.0.1", 9222))
        sock.close()

        if result == 0:
            # Port is open, now try to connect with Selenium
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_experimental_option(
                    "debuggerAddress", "127.0.0.1:9222"
                )
                driver = webdriver.Chrome(options=chrome_options)
                _ = driver.window_handles
                self.driver = driver
                # Pass log_callback to StampsAutomation
                self.automation_instance = StampsAutomation(
                    self.driver, self.stop_event, self.log_callback
                )
                print(
                    "Successfully connected to existing Chrome instance."
                )  # This print will still go to console
                self.after(0, self.update_status, "● Connected to Chrome", "#28a745")
            except Exception as e:
                self.driver = None
                self.automation_instance = None
                print(
                    f"Port 9222 is open, but connection failed: {e}"
                )  # This print will still go to console
                self.after(
                    0,
                    self.update_status,
                    "● Connection Error. Please 'Prepare Chrome'.",
                    "#ffc107",
                )
        else:
            # Port is not open
            self.driver = None
            self.automation_instance = None
            if not is_retrying:
                print(
                    "No active Chrome instance found."
                )  # This print will still go to console
                self.after(
                    0,
                    self.update_status,
                    "● Disconnected. Use 'Prepare Chrome' to start.",
                    "#6c757d",
                )

    def attempt_reconnect_to_chrome(self, is_retrying=False):
        """
        Starts the connection check in a separate thread to keep the UI responsive.
        The 'is_retrying' flag prevents certain messages from appearing after a launch attempt.
        """
        if not is_retrying:
            self.update_status("Checking for Chrome...", "#ffc107")

        thread = threading.Thread(
            target=self._threaded_chrome_check, args=(is_retrying,), daemon=True
        )
        thread.start()

    def create_main_widgets(self):
        """Creates the main notebook, tabs, and status bar."""
        # Status Bar
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

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        company_tab_frame = ttk.Frame(self.notebook)
        insurance_tab_frame = ttk.Frame(self.notebook)
        automation_tab_frame = ttk.Frame(self.notebook)

        self.notebook.add(company_tab_frame, text="Company Information")
        self.notebook.add(insurance_tab_frame, text="Insurance Company Information")
        self.notebook.add(automation_tab_frame, text="Automation Steps")

        self.company_tab_ui = CompanyTab(company_tab_frame, self)
        self.insurance_tab_ui = InsuranceTab(insurance_tab_frame, self)
        self.automation_tab_ui = AutomationTab(
            automation_tab_frame, self
        )  # Ensure this is initialized before log_callback is set

    def start_full_automation(self):
        """A central method to start the automation, called from any tab."""
        # Before starting, clear any previous stop signals
        self.stop_event.clear()
        if hasattr(self, "automation_tab_ui") and self.automation_tab_ui:
            self.automation_tab_ui.start_full_automation()
        else:
            messagebox.showerror("Error", "Automation components are not ready.")

    def stop_automation(self):
        """Method to set the stop event and signal the automation thread to stop."""
        if messagebox.askyesno(
            "Stop Automation",
            "Are you sure you want to stop the current automation process?",
        ):
            self.stop_event.set()  # Set the event to signal the thread to stop
            self.update_status("Stopping automation...", "#ffc107")  # Yellow
            if self.log_callback:  # Log to UI if callback is available
                self.log_callback("User requested to stop automation.")
            self.update_status(
                "● Automation stop signal sent. Chrome remains open.", "#6c757d"
            )  # Grey

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
