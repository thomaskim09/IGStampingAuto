import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import database
import pdf_processor


class IGStampingAuto(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IG Stamping Automation")
        self.geometry("800x650")

        # --- Style Configuration ---
        style = ttk.Style(self)
        style.theme_use("clam")

        # NEW: Define custom styles for colored buttons
        # Style for the 'Save' button (light green)
        style.configure(
            "Success.TButton",
            background="#d4edda",
            foreground="#155724",
            bordercolor="#c3e6cb",
        )
        # Style for the 'Delete' button (light red)
        style.configure(
            "Danger.TButton",
            background="#f8d7da",
            foreground="#721c24",
            bordercolor="#f5c6cb",
        )

        # --- Database Setup on Startup ---
        database.create_tables()
        database.add_default_insurance_if_empty()

        # (The rest of the __init__ method is unchanged)
        self.all_company_names = []
        self.all_insurance_names = []
        self.company_search_var = tk.StringVar()
        self.company_name = tk.StringVar()
        self.company_address = None
        self.company_old_roc = tk.StringVar()
        self.company_new_roc = tk.StringVar()
        self.company_phone = tk.StringVar()
        self.source_pdf_var = tk.StringVar()
        self.export_dir_var = tk.StringVar()
        self.company_combo = None
        self.uploaded_pdf_path = None
        self.insurance_search_var = tk.StringVar()
        self.insurance_name = tk.StringVar()
        self.insurance_address = None
        self.insurance_old_roc = tk.StringVar()
        self.insurance_new_roc = tk.StringVar()
        self.insurance_phone = tk.StringVar()
        self.insurance_combo = None
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        self.company_tab = ttk.Frame(self.notebook)
        self.insurance_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.company_tab, text="Company Information")
        self.notebook.add(self.insurance_tab, text="Insurance Company Information")
        self.create_company_widgets()
        self.create_insurance_widgets()
        self.load_company_names_to_search()
        self.load_insurance_names_to_search()
        self.auto_populate_default_insurance()

    def create_company_widgets(self):
        main_frame = ttk.Frame(self.company_tab, padding=10)
        main_frame.pack(expand=True, fill="both")

        # (Search frame and form frame are unchanged)
        search_frame = ttk.LabelFrame(
            main_frame, text="Search & File Paths", padding=10
        )
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search Company:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.company_combo = ttk.Combobox(
            search_frame, textvariable=self.company_search_var, values=[]
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
            search_frame, textvariable=self.source_pdf_var, state="disabled"
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(search_frame, text="Upload...", command=self.upload_pdf).grid(
            row=1, column=2, sticky="e", padx=5, pady=5
        )
        ttk.Label(search_frame, text="Export Directory:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            search_frame, textvariable=self.export_dir_var, state="disabled"
        ).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(search_frame, text="Browse...", command=self.select_export_dir).grid(
            row=2, column=2, sticky="e", padx=5, pady=5
        )
        form_frame = ttk.LabelFrame(main_frame, text="Company Details", padding=15)
        form_frame.pack(fill="x", expand=True, side="top", padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)
        ttk.Label(form_frame, text="Company Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.company_name).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="Address:").grid(
            row=1, column=0, sticky="nw", padx=5, pady=5
        )
        self.company_address = tk.Text(form_frame, height=4, width=40)
        self.company_address.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="Old ROC Number:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.company_old_roc).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="New ROC Number:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.company_new_roc).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="Telephone Number:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.company_phone).grid(
            row=4, column=1, sticky="ew", padx=5, pady=5
        )

        # --- UPDATED Button Layout and Style ---
        # A single frame for all buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 5), padx=5)

        # Pack Start Automation to the right first
        ttk.Button(
            button_frame, text="Start Automation", command=self.start_automation
        ).pack(side="right")

        # Pack data buttons to the left
        ttk.Button(
            button_frame, text="Clear Form", command=self.clear_company_form
        ).pack(side="left")
        # Apply the custom styles to Save and Delete buttons
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

    def create_insurance_widgets(self):
        # Updated this tab for layout consistency
        main_frame = ttk.Frame(self.insurance_tab, padding=10)
        main_frame.pack(expand=True, fill="both")

        search_frame = ttk.LabelFrame(
            main_frame, text="Search Insurance Company", padding=10
        )
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Search Company:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.insurance_combo = ttk.Combobox(
            search_frame, textvariable=self.insurance_search_var, values=[]
        )
        self.insurance_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.insurance_combo.bind("<<ComboboxSelected>>", self.populate_insurance_form)
        self.insurance_combo.bind("<KeyRelease>", self.on_insurance_search_type)

        form_frame = ttk.LabelFrame(
            main_frame, text="Insurance Company Details", padding=15
        )
        form_frame.pack(fill="x", expand=True, side="top", padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)
        ttk.Label(form_frame, text="Company Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.insurance_name).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="Address:").grid(
            row=1, column=0, sticky="nw", padx=5, pady=5
        )
        self.insurance_address = tk.Text(form_frame, height=4, width=40)
        self.insurance_address.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="Old ROC Number:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.insurance_old_roc).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="New ROC Number:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.insurance_new_roc).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="Telephone Number:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.insurance_phone).grid(
            row=4, column=1, sticky="ew", padx=5, pady=5
        )

        # Aligned buttons to the left for this tab
        data_button_frame = ttk.Frame(main_frame)
        data_button_frame.pack(fill="x", pady=5, padx=5)
        ttk.Button(
            data_button_frame, text="Clear Form", command=self.clear_insurance_form
        ).pack(side="left")
        ttk.Button(
            data_button_frame,
            text="Save Insurance Co.",
            style="Success.TButton",
            command=self.save_insurance,
        ).pack(side="left", padx=5)
        ttk.Button(
            data_button_frame,
            text="Delete Insurance Co.",
            style="Danger.TButton",
            command=self.delete_insurance,
        ).pack(side="left")

    # (All other methods remain unchanged from the previous version)
    def auto_populate_default_insurance(self):
        if self.all_insurance_names:
            first_company_name = self.all_insurance_names[0]
            self.insurance_search_var.set(first_company_name)
            self.populate_insurance_form()

    def on_company_search_type(self, event):
        typed_text = self.company_search_var.get().lower()
        if not typed_text:
            filtered_list = self.all_company_names
        else:
            filtered_list = [
                name
                for name in self.all_company_names
                if name.lower().startswith(typed_text)
            ]
        self.company_combo["values"] = filtered_list

    def on_insurance_search_type(self, event):
        typed_text = self.insurance_search_var.get().lower()
        if not typed_text:
            filtered_list = self.all_insurance_names
        else:
            filtered_list = [
                name
                for name in self.all_insurance_names
                if name.lower().startswith(typed_text)
            ]
        self.insurance_combo["values"] = filtered_list

    def load_company_names_to_search(self):
        self.all_company_names = database.get_all_company_names()
        if self.company_combo:
            self.company_combo["values"] = self.all_company_names

    def load_insurance_names_to_search(self):
        self.all_insurance_names = database.get_all_insurance_company_names()
        if self.insurance_combo:
            self.insurance_combo["values"] = self.all_insurance_names

    def clear_company_form(self):
        self.company_search_var.set("")
        self.company_name.set("")
        self.company_old_roc.set("")
        self.company_new_roc.set("")
        self.company_phone.set("")
        self.company_address.delete("1.0", "end")
        self.source_pdf_var.set("")
        self.export_dir_var.set("")
        self.uploaded_pdf_path = None

    def clear_insurance_form(self):
        self.insurance_search_var.set("")
        self.insurance_name.set("")
        self.insurance_old_roc.set("")
        self.insurance_new_roc.set("")
        self.insurance_phone.set("")
        self.insurance_address.delete("1.0", "end")

    def populate_company_form(self, event=None):
        selected_company = self.company_search_var.get()
        data = database.get_company_by_name(selected_company)
        if data:
            self.company_name.set(data.get("name", ""))
            self.company_old_roc.set(data.get("old_roc", ""))
            self.company_new_roc.set(data.get("new_roc", ""))
            self.company_phone.set(data.get("phone", ""))
            self.company_address.delete("1.0", "end")
            self.company_address.insert("1.0", data.get("address", ""))

    def populate_insurance_form(self, event=None):
        selected_company = self.insurance_search_var.get()
        data = database.get_insurance_company_by_name(selected_company)
        if data:
            self.insurance_name.set(data.get("name", ""))
            self.insurance_old_roc.set(data.get("old_roc", ""))
            self.insurance_new_roc.set(data.get("new_roc", ""))
            self.insurance_phone.set(data.get("phone", ""))
            self.insurance_address.delete("1.0", "end")
            self.insurance_address.insert("1.0", data.get("address", ""))

    def select_export_dir(self):
        dir_path = filedialog.askdirectory(title="Select Export Directory")
        if dir_path:
            self.export_dir_var.set(dir_path)

    def upload_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Select a PDF file", filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return
        self.uploaded_pdf_path = filepath
        self.source_pdf_var.set(filepath)
        self.export_dir_var.set(os.path.dirname(filepath))
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
            self.company_search_var.set(company_name_from_pdf)
            self.populate_company_form()
            messagebox.showinfo(
                "Company Found",
                f"Found '{company_name_from_pdf}' in the database and populated the form.",
            )
        else:
            self.company_name.set(company_name_from_pdf)
            self.company_address.delete("1.0", "end")
            self.company_address.insert("1.0", extracted_data.get("address", ""))
            messagebox.showinfo(
                "New Company Detected",
                "Extracted new company info from PDF. Please review and save.",
            )

    def save_company(self):
        name = self.company_name.get()
        if not name:
            messagebox.showerror("Error", "Company Name cannot be empty.")
            return
        database.add_company(
            name,
            self.company_address.get("1.0", "end-1c"),
            self.company_old_roc.get(),
            self.company_new_roc.get(),
            self.company_phone.get(),
        )
        self.load_company_names_to_search()
        self.company_search_var.set(name)
        messagebox.showinfo("Success", f"Company '{name}' saved successfully.")

    def delete_company(self):
        name = self.company_name.get()
        if not name:
            messagebox.showerror("Error", "No company selected to delete.")
        elif messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{name}'?"
        ):
            database.delete_company(name)
            self.clear_company_form()
            self.load_company_names_to_search()
            messagebox.showinfo("Success", f"Company '{name}' deleted successfully.")

    def save_insurance(self):
        name = self.insurance_name.get()
        if not name:
            messagebox.showerror("Error", "Insurance Company Name cannot be empty.")
            return
        database.add_insurance_company(
            name,
            self.insurance_address.get("1.0", "end-1c"),
            self.insurance_old_roc.get(),
            self.insurance_new_roc.get(),
            self.insurance_phone.get(),
        )
        self.load_insurance_names_to_search()
        self.insurance_search_var.set(name)
        messagebox.showinfo(
            "Success", f"Insurance Company '{name}' saved successfully."
        )

    def delete_insurance(self):
        name = self.insurance_name.get()
        if not name:
            messagebox.showerror("Error", "No insurance company selected to delete.")
        elif messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{name}'?"
        ):
            database.delete_insurance_company(name)
            self.clear_insurance_form()
            self.load_insurance_names_to_search()
            messagebox.showinfo(
                "Success", f"Insurance Company '{name}' deleted successfully."
            )

    def start_automation(self):
        if not self.uploaded_pdf_path:
            messagebox.showerror("Error", "Please upload a PDF first.")
            return
        company_name = self.company_name.get()
        if not company_name:
            messagebox.showerror("Error", "No company information loaded.")
            return
        website_id = "FWCMS-ID-987654321"
        roc_text = self.company_new_roc.get() or self.company_old_roc.get()
        if not roc_text:
            messagebox.showwarning(
                "Warning", "ROC number is missing. It will not be added to the PDF."
            )
        output_dir = self.export_dir_var.get()
        if not output_dir:
            messagebox.showerror(
                "Error",
                "Export directory is not set. Please upload a PDF or select a directory.",
            )
            return
        pdf_filename = os.path.basename(self.uploaded_pdf_path)
        output_filename = f"{company_name}_{pdf_filename}"
        output_path = os.path.join(output_dir, output_filename)
        success = pdf_processor.add_labels_to_pdf(
            source_path=self.uploaded_pdf_path,
            output_path=output_path,
            unique_id=website_id,
            roc_text=f"ROC: {roc_text}",
            custom_text="For LHDN Stamping",
        )
        if not success:
            messagebox.showerror("Error", "Failed to add labels to the PDF.")
            return
        messagebox.showinfo(
            "PDF Processed", f"Successfully created labeled PDF:\n{output_path}"
        )
        print("--- Next Step: Web Automation ---")
        print(
            f"Would now proceed to automate the website using this file: {output_path}"
        )


if __name__ == "__main__":
    app = IGStampingAuto()
    app.mainloop()
