import platform
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
from selenium import webdriver
from PIL import Image, ImageTk

# Local module imports
import database
import pdf_processor
from automation import StampsAutomation


# --- Helper function to find data files ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None


class CompanyTab:
    def __init__(self, parent_tab, app):
        self.parent_tab = parent_tab
        self.app = app
        self.popup_widgets = {}
        self.current_step = 0
        self.steps_data = []
        self.photo_image = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.parent_tab, padding=10)
        main_frame.pack(expand=True, fill="both")

        search_frame = ttk.LabelFrame(
            main_frame, text="Search & File Paths", padding=10
        )
        search_frame.pack(fill="x", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Source PDF:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            search_frame, textvariable=self.app.source_pdf_var, state="disabled"
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(search_frame, text="Upload...", command=self.upload_pdf).grid(
            row=0, column=2, sticky="e", padx=5, pady=5
        )

        ttk.Label(search_frame, text="Export Directory:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            search_frame, textvariable=self.app.export_dir_var, state="disabled"
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(search_frame, text="Browse...", command=self.select_export_dir).grid(
            row=1, column=2, sticky="e", padx=5, pady=5
        )

        ttk.Label(search_frame, text="Search Company:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.company_combo = ttk.Combobox(
            search_frame, textvariable=self.app.company_search_var, values=[]
        )
        self.company_combo.grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )
        self.company_combo.bind("<<ComboboxSelected>>", self.populate_company_form)
        self.company_combo.bind("<KeyRelease>", self.on_company_search_type)

        ttk.Label(search_frame, text="Policy Number:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(search_frame, textvariable=self.app.policy_number).grid(
            row=3, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(search_frame, text="Adjudication Number:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        adjudikasi_entry = ttk.Entry(search_frame, textvariable=self.app.adjudikasi_id)
        adjudikasi_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        ToolTip(
            adjudikasi_entry,
            "This will be auto-fetched from the website during automation.",
        )

        generate_pdf_button = ttk.Button(
            search_frame, text="Generate Labeled PDF", command=self.add_remark_to_pdf
        )
        generate_pdf_button.grid(row=4, column=2, sticky="e", padx=5, pady=5)
        ToolTip(
            generate_pdf_button,
            "Manual PDF generation. A remarked PDF is automatically created in the export directory when automation starts.",
        )
        form_frame = ttk.LabelFrame(main_frame, text="Company Details", padding=15)
        form_frame.pack(fill="x", expand=True, side="top", padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Company Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_name).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
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
        ttk.Label(form_frame, text="Postcode:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_postcode).grid(
            row=4, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="City:").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_city).grid(
            row=5, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="State:").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_state).grid(
            row=6, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="Old ROC Number:").grid(
            row=7, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_old_roc).grid(
            row=7, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="New ROC Number:").grid(
            row=8, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_new_roc).grid(
            row=8, column=1, sticky="ew", padx=5, pady=5
        )
        ttk.Label(form_frame, text="Telephone Number:").grid(
            row=9, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(form_frame, textvariable=self.app.company_phone).grid(
            row=9, column=1, sticky="ew", padx=5, pady=5
        )

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
            button_frame,
            text="Check Chrome",
            command=self.app.attempt_reconnect_to_chrome,
        ).pack(side="right")

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

    def _threaded_prepare_chrome(self):
        """Launches and connects to Chrome in a background thread to prevent UI freeze."""
        try:
            self.app.after(
                0, self.app.update_status, "Connecting to Chrome...", "#ffc107"
            )
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            service = webdriver.chrome.service.Service()
            service.start()
            driver = webdriver.Remote(service.service_url, options=chrome_options)
            _ = driver.window_handles
            self.app.driver = driver
            self.app.automation_instance = StampsAutomation(
                self.app.driver, self.app.stop_event, self.app.log_callback
            )
            self.app.after(
                0, self.app.update_status, "● Connected to Chrome", "#28a745"
            )
            # Always show the popup, even if successfully connected.
            self.app.after(0, self.show_startup_info_popup)
            return
        except Exception:
            self.app.after(
                0,
                self.app.update_status,
                "No instance found. Launching Chrome...",
                "#17a2b8",
            )
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
            self.app.after(0, self.show_startup_info_popup)
            self.app.attempt_reconnect_to_chrome(is_retrying=True)
        except FileNotFoundError:
            self.app.after(
                0,
                self.app.update_status,
                "● Disconnected. Chrome not found.",
                "#dc3545",
            )
            self.app.after(
                0, messagebox.showerror, "Error", "Could not find 'chrome.exe'."
            )
        except Exception as e:
            self.app.after(
                0,
                self.app.update_status,
                "● Disconnected. Failed to connect.",
                "#dc3545",
            )
            self.app.after(
                0, messagebox.showerror, "Error", f"Failed to prepare Chrome: {e}"
            )
            self.app.driver = None
            self.app.automation_instance = None

    def prepare_chrome(self):
        threading.Thread(target=self._threaded_prepare_chrome, daemon=True).start()

    def _next_step(self):
        self.current_step += 1
        self._update_step_view()

    def _prev_step(self):
        self.current_step -= 1
        self._update_step_view()

    def _update_step_view(self):
        step_info = self.steps_data[self.current_step]
        image_path = step_info["image"]

        if os.path.exists(image_path):
            img = Image.open(image_path)
            img.thumbnail((780, 500))
            self.photo_image = ImageTk.PhotoImage(img)
            self.popup_widgets["img_label"].config(image=self.photo_image)
        else:
            self.popup_widgets["img_label"].config(
                image=None, text=f"Image not found:\n{image_path}"
            )

        self.popup_widgets["text_label"].config(text=step_info["text"])

        self.popup_widgets["prev_button"].config(
            state="normal" if self.current_step > 0 else "disabled"
        )

        if self.current_step == len(self.steps_data) - 1:
            self.popup_widgets["next_button"].pack_forget()
            self.popup_widgets["ok_button"].pack(side="right", padx=10)
        else:
            self.popup_widgets["ok_button"].pack_forget()
            self.popup_widgets["next_button"].pack(side="right", padx=10)

    def show_startup_info_popup(self):
        self.steps_data = [
            {
                "image": resource_path(os.path.join("resource", "startup_page.jpg")),
                "text": "Step 1: Please start a new 'Permohonan Am', select the correct 'Negeri', and choose the date based on the IG PDF.",
            },
            {
                "image": resource_path(os.path.join("resource", "startup_image_2.jpg")),
                "text": "Step 2: Before starting the automation, please ensure you have navigated to this page to fill in the company details. This is the starting page for the automation.",
            },
        ]
        self.current_step = 0

        # Check if a popup from a previous click is still open
        if (
            self.popup_widgets
            and self.popup_widgets.get("window")
            and self.popup_widgets["window"].winfo_exists()
        ):
            self.popup_widgets["window"].lift()
            return

        popup = tk.Toplevel(self.app)
        popup.title("Chrome Setup Instructions")
        popup.attributes("-topmost", True)
        popup.geometry("800x650")
        popup.resizable(False, False)

        popup.update_idletasks()
        width, height = popup.winfo_width(), popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        img_label = ttk.Label(popup)
        img_label.pack(pady=10)

        text_label = ttk.Label(
            popup, wraplength=780, justify="center", font=("Segoe UI", 10)
        )
        text_label.pack(pady=10, padx=10, fill="x")

        separator = ttk.Separator(popup, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=5)

        button_frame = ttk.Frame(popup, padding=10)
        button_frame.pack(fill="x", side="bottom")

        ok_button = ttk.Button(
            button_frame, text="Finish", command=popup.destroy, style="Success.TButton"
        )
        next_button = ttk.Button(button_frame, text="Next →", command=self._next_step)
        prev_button = ttk.Button(
            button_frame, text="← Previous", command=self._prev_step
        )
        prev_button.pack(side="left", padx=10)

        self.popup_widgets = {
            "window": popup,  # Keep a reference to the window itself
            "img_label": img_label,
            "text_label": text_label,
            "prev_button": prev_button,
            "next_button": next_button,
            "ok_button": ok_button,
        }

        self._update_step_view()

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
        self.app.adjudikasi_id.set("")
        self.app.policy_number.set("")

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
        self.clear_company_form()
        self.app.uploaded_pdf_path = filepath
        self.app.source_pdf_var.set(filepath)
        source_directory = os.path.dirname(filepath)
        output_directory = os.path.join(source_directory, "output_stamped")
        self.app.export_dir_var.set(output_directory)

        extracted_data = pdf_processor.extract_info_from_pdf(filepath)

        if extracted_data.get("policy_number"):
            self.app.policy_number.set(extracted_data.get("policy_number"))

        if not extracted_data or not extracted_data.get("name"):
            messagebox.showwarning(
                "PDF Read Failed",
                "Could not automatically find a company name in the PDF.",
            )
            return

        company_name_from_pdf = extracted_data.get("name")
        first_word = company_name_from_pdf.split()[0].lower()
        found_match = False
        for company_name in self.app.all_company_names:
            if company_name.lower().startswith(first_word):
                self.app.company_search_var.set(company_name)
                self.populate_company_form()
                messagebox.showinfo(
                    "Company Matched",
                    f"Found a likely match '{company_name}' in the database.",
                )
                found_match = True
                break
        if not found_match:
            self.app.company_name.set(company_name_from_pdf)
            messagebox.showinfo(
                "New Company Detected",
                "No close match found. Extracted new company info from PDF.",
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

    def add_remark_to_pdf(self):
        source_pdf = self.app.uploaded_pdf_path
        unique_id = self.app.adjudikasi_id.get()
        old_roc = self.app.company_old_roc.get()
        new_roc = self.app.company_new_roc.get()
        roc_text = f"{new_roc}/{old_roc}"
        if not all([source_pdf, unique_id, old_roc, new_roc]):
            messagebox.showerror(
                "Missing Information",
                "Please ensure a Source PDF is uploaded, the Adjudication Number and both ROC number fields are filled.",
            )
            return
        output_folder = self.app.export_dir_var.get()
        os.makedirs(output_folder, exist_ok=True)
        pdf_filename = os.path.basename(source_pdf)
        output_path = os.path.join(output_folder, pdf_filename)
        success = pdf_processor.add_labels_to_pdf(
            source_path=source_pdf,
            output_path=output_path,
            unique_id=unique_id,
            roc_text=roc_text,
        )
        if success:
            messagebox.showinfo(
                "PDF Generated",
                f"Successfully generated labeled PDF at:\n{output_path}",
            )
            try:
                if platform.system() == "Windows":
                    os.startfile(output_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", output_path])
                else:
                    subprocess.Popen(["xdg-open", output_path])
            except Exception as e:
                messagebox.showerror(
                    "Error Opening PDF",
                    f"Failed to open the PDF automatically.\nError: {e}",
                )
        else:
            messagebox.showerror("PDF Generation Failed", "Could not label the PDF.")
