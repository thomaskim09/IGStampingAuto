# ui_company_tab.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
from PIL import Image, ImageTk

# Local module imports
import database
import pdf_processor
import automation


class CompanyTab:
    def __init__(self, parent_tab, app):
        """
        Initializes the Company Information Tab UI and its logic.
        :param parent_tab: The parent ttk.Frame (the tab itself).
        :param app: The main application instance (IGStampingAuto).
        """
        self.parent_tab = parent_tab
        self.app = app  # Main application instance
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.parent_tab, padding=10)
        main_frame.pack(expand=True, fill="both")

        # --- Search and File Paths Frame ---
        search_frame = ttk.LabelFrame(
            main_frame, text="Search & File Paths", padding=10
        )
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search Company:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.company_combo = ttk.Combobox(
            search_frame, textvariable=self.app.company_search_var, values=[]
        )
        self.company_combo.grid(
            row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.company_combo.bind("<<ComboboxSelected>>", self.populate_company_form)
        self.company_combo.bind("<KeyRelease>", self.on_company_search_type)

        ttk.Label(search_frame, text="Source PDF:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            search_frame, textvariable=self.app.source_pdf_var, state="disabled"
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(search_frame, text="Upload...", command=self.upload_pdf).grid(
            row=1, column=2, sticky="e", padx=5, pady=5
        )

        ttk.Label(search_frame, text="Export Directory:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            search_frame, textvariable=self.app.export_dir_var, state="disabled"
        ).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(search_frame, text="Browse...", command=self.select_export_dir).grid(
            row=2, column=2, sticky="e", padx=5, pady=5
        )

        # --- Company Details Form Frame ---
        form_frame = ttk.LabelFrame(main_frame, text="Company Details", padding=15)
        form_frame.pack(fill="x", expand=True, side="top", padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)

        # --- RE-ORDERED WIDGETS TO MATCH THE IMAGE ---
        # Row 0: Company Name
        ttk.Label(form_frame, text="Company Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_name).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 1-3: Address Lines
        ttk.Label(form_frame, text="Address 1:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_address1).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Address 2:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_address2).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Address 3:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_address3).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 4: Postcode
        ttk.Label(form_frame, text="Postcode:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_postcode).grid(
            row=4, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 5: City
        ttk.Label(form_frame, text="City:").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_city).grid(
            row=5, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 6: State
        ttk.Label(form_frame, text="State:").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_state).grid(
            row=6, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 7: Old ROC
        ttk.Label(form_frame, text="Old ROC Number:").grid(
            row=7, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_old_roc).grid(
            row=7, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 8: New ROC
        ttk.Label(form_frame, text="New ROC Number:").grid(
            row=8, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_new_roc).grid(
            row=8, column=1, sticky="ew", padx=5, pady=5
        )

        # Row 9: Telephone
        ttk.Label(form_frame, text="Telephone Number:").grid(
            row=9, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_phone).grid(
            row=9, column=1, sticky="ew", padx=5, pady=5
        )

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 5), padx=5)

        ttk.Button(
            button_frame,
            text="Start Automation",
            command=self.app.start_full_automation,
        ).pack(side="right")
        ttk.Button(
            button_frame, text="Prepare Chrome", command=self.prepare_chrome
        ).pack(side="right", padx=5)

        ttk.Button(
            button_frame, text="Clear Form", command=self.clear_company_form
        ).pack(side="left")
        ttk.Button(
            button_frame,
            text="Save Company",
            style="Success.TButton",
            command=self.save_company,
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Delete Company",
            style="Danger.TButton",
            command=self.delete_company,
        ).pack(side="left")

    def show_startup_info_popup(self):
        image_path = os.path.join("resource", "startup_page.jpg")
        if not os.path.exists(image_path):
            messagebox.showwarning(
                "Image Not Found",
                f"Could not find '{image_path}'.\nPlease make sure the screenshot exists in the 'resource' folder.",
            )
            return

        popup = tk.Toplevel(self.app)
        popup.title("Chrome Prepared")
        popup.geometry("600x450")
        img = Image.open(image_path)
        img.thumbnail((580, 350))
        photo = ImageTk.PhotoImage(img)
        img_label = ttk.Label(popup, image=photo)
        img_label.image = photo
        img_label.pack(pady=10)
        text_label = ttk.Label(
            popup,
            text="Please log in and navigate to the correct page in the new Chrome window.",
            wraplength=580,
        )
        text_label.pack(pady=5)
        ok_button = ttk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)
        popup.transient(self.app)
        popup.grab_set()
        self.app.wait_window(popup)

    def prepare_chrome(self):
        profile_path = os.path.join(os.getcwd(), "chrome_profile")
        target_website = "https://stamps.hasil.gov.my/stamps/"
        command = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "--remote-debugging-port=9222",
            f"--user-data-dir={profile_path}",
            target_website,
        ]
        try:
            subprocess.Popen(command)
            self.show_startup_info_popup()

            chrome_options = automation.webdriver.chrome.options.Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.app.driver = automation.webdriver.Chrome(options=chrome_options)
            self.app.automation_instance = automation.StampsAutomation(self.app.driver)
            messagebox.showinfo("Success", "Successfully connected to Chrome.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare Chrome or connect: {e}")
            self.app.driver = None
            self.app.automation_instance = None

    def on_company_search_type(self, event):
        typed_text = self.app.company_search_var.get().lower()
        filtered_list = [
            name
            for name in self.app.all_company_names
            if name.lower().startswith(typed_text)
        ]
        self.company_combo["values"] = filtered_list

    def clear_company_form(self):
        self.app.company_search_var.set("")
        self.app.company_name.set("")
        self.app.company_address1.set("")
        self.app.company_address2.set("")
        self.app.company_address3.set("")
        self.app.company_postcode.set("")
        self.app.company_city.set("")
        self.app.company_state.set("")
        self.app.company_old_roc.set("")
        self.app.company_new_roc.set("")
        self.app.company_phone.set("")
        self.app.source_pdf_var.set("")
        self.app.export_dir_var.set("")
        self.app.uploaded_pdf_path = None

    def populate_company_form(self, event=None):
        selected_company = self.app.company_search_var.get()
        data = database.get_company_by_name(selected_company)
        if data:
            self.app.company_name.set(data.get("name", ""))
            self.app.company_address1.set(data.get("address_1", ""))
            self.app.company_address2.set(data.get("address_2", ""))
            self.app.company_address3.set(data.get("address_3", ""))
            self.app.company_postcode.set(data.get("postcode", ""))
            self.app.company_city.set(data.get("city", ""))
            self.app.company_state.set(data.get("state", ""))
            self.app.company_old_roc.set(data.get("old_roc", ""))
            self.app.company_new_roc.set(data.get("new_roc", ""))
            self.app.company_phone.set(data.get("phone", ""))

    def select_export_dir(self):
        dir_path = filedialog.askdirectory(title="Select Export Directory")
        if dir_path:
            self.app.export_dir_var.set(dir_path)

    def upload_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Select a PDF file", filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return
        self.app.uploaded_pdf_path = filepath
        self.app.source_pdf_var.set(filepath)
        self.app.export_dir_var.set(self.app.output_dir_path)
        extracted_data = pdf_processor.extract_info_from_pdf(filepath)
        if not extracted_data or not extracted_data.get("name"):
            messagebox.showwarning(
                "PDF Read Failed",
                "Could not automatically find a company name in the PDF.",
            )
            return
        company_name_from_pdf = extracted_data.get("name")
        db_match = database.get_company_by_name(company_name_from_pdf)
        if db_match:
            self.app.company_search_var.set(company_name_from_pdf)
            self.populate_company_form()
            messagebox.showinfo(
                "Company Found", f"Found '{company_name_from_pdf}' in the database."
            )
        else:
            self.app.company_name.set(company_name_from_pdf)
            messagebox.showinfo(
                "New Company Detected",
                "Extracted new company info from PDF. Please review and save the full address.",
            )

    def save_company(self):
        name = self.app.company_name.get()
        if not name:
            messagebox.showerror("Error", "Company Name cannot be empty.")
            return
        database.add_company(
            name=name,
            address_1=self.app.company_address1.get(),
            address_2=self.app.company_address2.get(),
            address_3=self.app.company_address3.get(),
            city=self.app.company_city.get(),
            postcode=self.app.company_postcode.get(),
            state=self.app.company_state.get(),
            phone=self.app.company_phone.get(),
            old_roc=self.app.company_old_roc.get(),
            new_roc=self.app.company_new_roc.get(),
        )
        self.app.load_company_names_to_search()
        self.app.company_search_var.set(name)
        messagebox.showinfo("Success", f"Company '{name}' saved successfully.")

    def delete_company(self):
        name = self.app.company_name.get()
        if not name:
            messagebox.showerror("Error", "No company selected to delete.")
        elif messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{name}'?"
        ):
            database.delete_company(name)
            self.clear_company_form()
            self.app.load_company_names_to_search()
            messagebox.showinfo("Success", f"Company '{name}' deleted successfully.")
