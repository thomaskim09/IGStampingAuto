# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import os

# Local module imports
import database
from ui_company_tab import CompanyTab
from ui_insurance_tab import InsuranceTab
from ui_automation_tab import AutomationTab


class IGStampingAuto(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IG Stamping Automation")
        self.geometry("800x700")

        # --- Core Application State Variables ---
        self.driver = None
        self.automation_instance = None
        self.adjudikasi_id = tk.StringVar()
        self.output_dir_path = os.path.join(os.getcwd(), "output_stamped")
        os.makedirs(self.output_dir_path, exist_ok=True)
        self.uploaded_pdf_path = None
        self.all_company_names = []
        self.all_insurance_names = []

        # --- Tkinter UI Variables (The Application's Data Model) ---
        self.company_search_var = tk.StringVar()
        self.company_name = tk.StringVar()
        self.company_old_roc = tk.StringVar()
        self.company_new_roc = tk.StringVar()
        self.company_phone = tk.StringVar()
        self.source_pdf_var = tk.StringVar()
        self.export_dir_var = tk.StringVar()
        self.insurance_search_var = tk.StringVar()
        self.insurance_name = tk.StringVar()
        self.insurance_old_roc = tk.StringVar()
        self.insurance_new_roc = tk.StringVar()
        self.insurance_phone = tk.StringVar()

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
        database.add_default_insurance_if_empty()

        # --- UI Initialization ---
        self.create_main_window()
        self.load_company_names_to_search()  # Initial data load
        self.load_insurance_names_to_search()
        self.auto_populate_default_insurance()  # This is the corrected call

    def create_main_window(self):
        """Creates the main notebook and populates tabs from other UI files."""
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
        self.automation_tab_ui = AutomationTab(automation_tab_frame, self)

    def start_full_automation(self):
        """A central method to start the automation, called from any tab."""
        if hasattr(self, "automation_tab_ui") and self.automation_tab_ui:
            self.automation_tab_ui.start_automation()
        else:
            messagebox.showerror("Error", "Automation components are not ready.")

    def load_company_names_to_search(self):
        self.all_company_names = database.get_all_company_names()
        if hasattr(self, "company_tab_ui") and self.company_tab_ui.company_combo:
            self.company_tab_ui.company_combo["values"] = self.all_company_names

    def load_insurance_names_to_search(self):
        self.all_insurance_names = database.get_all_insurance_company_names()
        if hasattr(self, "insurance_tab_ui") and self.insurance_tab_ui.insurance_combo:
            self.insurance_tab_ui.insurance_combo["values"] = self.all_insurance_names

    def auto_populate_default_insurance(self):
        """
        Gets the first insurance company from the DB and tells the UI tab
        to populate its form with that data.
        """
        # This check ensures the UI has been built before we try to access it
        if hasattr(self, "insurance_tab_ui"):
            # Get the default name from the database
            names = database.get_all_insurance_company_names()
            if names:
                # Set the search variable in the main app
                self.insurance_search_var.set(names[0])
                # Call the correct, existing function in the UI tab
                self.insurance_tab_ui.populate_insurance_form()


if __name__ == "__main__":
    app = IGStampingAuto()
    app.mainloop()
