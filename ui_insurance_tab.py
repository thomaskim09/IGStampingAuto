# ui_insurance_tab.py

from tkinter import ttk, messagebox
import database


class InsuranceTab:
    def __init__(self, parent_tab, app):
        """
        Initializes the Insurance Company Tab UI and its logic.
        """
        self.parent_tab = parent_tab
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.parent_tab, padding=10)
        main_frame.pack(expand=True, fill="both")

        # --- Search Frame ---
        search_frame = ttk.LabelFrame(
            main_frame, text="Search Insurance Company", padding=10
        )
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search Company:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.insurance_combo = ttk.Combobox(
            search_frame, textvariable=self.app.insurance_search_var, values=[]
        )
        self.insurance_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.insurance_combo.bind("<<ComboboxSelected>>", self.populate_insurance_form)
        self.insurance_combo.bind("<KeyRelease>", self.on_insurance_search_type)

        # --- Details Form ---
        form_frame = ttk.LabelFrame(
            main_frame, text="Insurance Company Details", padding=15
        )
        form_frame.pack(fill="x", expand=True, side="top", padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Company Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_name).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )

        # New Structured Address Fields
        ttk.Label(form_frame, text="Address 1:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_address1).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Address 2:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_address2).grid(
            row=2, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Address 3:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_address3).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Postcode:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_postcode).grid(
            row=4, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="City:").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_city).grid(
            row=5, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="State:").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_state).grid(
            row=6, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Old ROC Number:").grid(
            row=7, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_old_roc).grid(
            row=7, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="New ROC Number:").grid(
            row=8, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_new_roc).grid(
            row=8, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(form_frame, text="Telephone Number:").grid(
            row=9, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.insurance_phone).grid(
            row=9, column=1, sticky="ew", padx=5, pady=5
        )

        # --- Button Frame ---
        data_button_frame = ttk.Frame(main_frame)
        data_button_frame.pack(fill="x", pady=10, padx=5)

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

    def on_insurance_search_type(self, event):
        typed_text = self.app.insurance_search_var.get().lower()
        filtered_list = [
            name
            for name in self.app.all_insurance_names
            if name.lower().startswith(typed_text)
        ]
        self.insurance_combo["values"] = filtered_list

    def clear_insurance_form(self):
        self.app.insurance_search_var.set("")
        self.app.insurance_name.set("")
        self.app.insurance_old_roc.set("")
        self.app.insurance_new_roc.set("")
        self.app.insurance_phone.set("")
        self.app.insurance_address1.set("")
        self.app.insurance_address2.set("")
        self.app.insurance_address3.set("")
        self.app.insurance_postcode.set("")
        self.app.insurance_city.set("")
        self.app.insurance_state.set("")

    def populate_insurance_form(self, event=None):
        selected_company = self.app.insurance_search_var.get()
        data = database.get_insurance_company_by_name(selected_company)
        if data:
            self.app.insurance_name.set(data.get("name", ""))
            self.app.insurance_old_roc.set(data.get("old_roc", ""))
            self.app.insurance_new_roc.set(data.get("new_roc", ""))
            self.app.insurance_phone.set(data.get("phone", ""))
            self.app.insurance_address1.set(data.get("address_1", ""))
            self.app.insurance_address2.set(data.get("address_2", ""))
            self.app.insurance_address3.set(data.get("address_3", ""))
            self.app.insurance_postcode.set(data.get("postcode", ""))
            self.app.insurance_city.set(data.get("city", ""))
            self.app.insurance_state.set(data.get("state", ""))

    def save_insurance(self):
        name = self.app.insurance_name.get()
        if not name:
            messagebox.showerror("Error", "Insurance Company Name cannot be empty.")
            return
        database.add_insurance_company(
            name=name,
            address_1=self.app.insurance_address1.get(),
            address_2=self.app.insurance_address2.get(),
            address_3=self.app.insurance_address3.get(),
            city=self.app.insurance_city.get(),
            postcode=self.app.insurance_postcode.get(),
            state=self.app.insurance_state.get(),
            phone=self.app.insurance_phone.get(),
            old_roc=self.app.insurance_old_roc.get(),
            new_roc=self.app.insurance_new_roc.get(),
        )
        self.app.load_insurance_names_to_search()
        self.app.insurance_search_var.set(name)
        messagebox.showinfo(
            "Success", f"Insurance Company '{name}' saved successfully."
        )

    def delete_insurance(self):
        name = self.app.insurance_name.get()
        if not name:
            messagebox.showerror("Error", "No insurance company selected to delete.")
        elif messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{name}'?"
        ):
            database.delete_insurance_company(name)
            self.clear_insurance_form()
            self.app.load_insurance_names_to_search()
            messagebox.showinfo(
                "Success", f"Insurance Company '{name}' deleted successfully."
            )
