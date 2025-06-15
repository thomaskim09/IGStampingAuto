from tkinter import ttk, messagebox, scrolledtext
import os
import threading
import pdf_processor
from selenium.common.exceptions import NoSuchWindowException, WebDriverException


class AutomationTab:
    def __init__(self, parent_tab, app):
        self.parent_tab = parent_tab
        self.app = app
        self.log_area = None
        self.create_widgets()

    def get_company_data_from_form(self):
        company_data = {
            "name": self.app.company_name.get(),
            "address_1": self.app.company_address1.get(),
            "address_2": self.app.company_address2.get(),
            "address_3": self.app.company_address3.get(),
            "city": self.app.company_city.get(),
            "postcode": self.app.company_postcode.get(),
            "state": self.app.company_state.get(),
            "phone": self.app.company_phone.get(),
            "old_roc": self.app.company_old_roc.get(),
            "new_roc": self.app.company_new_roc.get(),
        }
        if not company_data["name"]:
            messagebox.showerror("Validation Error", "Company Name is required.")
            return None
        return company_data

    def get_insurance_data_from_form(self):
        insurance_data = {
            "name": self.app.insurance_name.get(),
            "address_1": self.app.insurance_address1.get(),
            "address_2": self.app.insurance_address2.get(),
            "address_3": self.app.insurance_address3.get(),
            "city": self.app.insurance_city.get(),
            "postcode": self.app.insurance_postcode.get(),
            "state": self.app.insurance_state.get(),
            "phone": self.app.insurance_phone.get(),
            "old_roc": self.app.insurance_old_roc.get(),
            "new_roc": self.app.insurance_new_roc.get(),
        }
        if not insurance_data["name"]:
            messagebox.showerror(
                "Validation Error", "Insurance Company Name is required."
            )
            return None
        return insurance_data

    def log_message(self, message):
        """Appends a message to the log area in a thread-safe way."""
        # Use app.after to ensure the update happens on the main Tkinter thread
        self.app.after(0, self._append_to_log_area, message)

    def _append_to_log_area(self, message):
        """Actual method to append text to the log area."""
        if self.log_area:
            self.log_area.configure(state="normal")
            self.log_area.insert("end", message + "\n")
            self.log_area.see("end")
            self.log_area.configure(state="disabled")

    def _handle_error(self, e):
        """A centralized function to handle automation errors."""
        error_string = str(e).lower()
        # Expanded list of keywords to detect a lost browser connection
        connection_error_keywords = [
            "no such window",
            "target window already closed",
            "disconnected",
            "cannot determine loading status",
            "message port closed",
            "stacktrace",  # Catches generic driver crashes
        ]

        if isinstance(e, (NoSuchWindowException, WebDriverException)) and any(
            keyword in error_string for keyword in connection_error_keywords
        ):
            custom_error_message = 'Connection to Chrome was lost. Please use the "Check Chrome" feature to reconnect, or the "Prepare Chrome" feature if Chrome was closed.'
            self.log_message(f"ERROR: {custom_error_message}")
            self.app.after(
                0, messagebox.showerror, "Connection Error", custom_error_message
            )
        else:
            # For all other errors, show the specific error message
            error_message = f"An unexpected error occurred: {str(e)}"
            self.log_message(f"ERROR: {error_message}")
            self.app.after(0, messagebox.showerror, "Automation Error", error_message)

    def _threaded_automation_runner(
        self, task_function, start_log_message, success_log_message, *args
    ):
        """
        A generic wrapper to run any automation task in a background thread.
        """
        self.log_message(start_log_message)
        try:
            result = task_function(*args)
            self.log_message(f"SUCCESS: {success_log_message}")
            if "Phase 1" in start_log_message and result:
                self.app.after(0, self.app.adjudikasi_id.set, result)
            self.app.after(0, messagebox.showinfo, "Success", success_log_message)
        except InterruptedError:
            self.log_message("WARNING: Automation process was stopped by the user.")
            self.app.after(
                0,
                messagebox.showwarning,
                "Automation Interrupted",
                "The automation process was stopped by the user.",
            )
        except Exception as e:
            self._handle_error(e)  # Use the centralized error handler
        finally:
            if self.app.driver and self.app.automation_instance:
                self.app.after(
                    0, self.app.update_status, "● Connected to Chrome", "#28a745"
                )
            else:
                self.app.after(0, self.app.update_status, "● Disconnected", "#6c757d")
            self.app.stop_event.clear()

    def start_automation_thread(
        self,
        task_function,
        start_log_message,
        success_log_message,
        *args,
    ):
        """
        Validates connection and starts the threaded automation runner.
        """
        if not self.app.automation_instance:
            messagebox.showerror(
                "Error", "Chrome is not prepared. Please connect first."
            )
            return

        self.app.stop_event.clear()
        self.app.update_status(
            start_log_message.replace("Starting task: ", "").replace("...", "..."),
            "#17a2b8",
        )
        threading.Thread(
            target=self._threaded_automation_runner,
            args=(
                task_function,
                start_log_message,
                success_log_message,
                *args,
            ),
            daemon=True,
        ).start()

    def create_widgets(self):
        """Creates and arranges all widgets in the automation tab."""
        main_frame = ttk.Frame(self.parent_tab, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Button(
            main_frame,
            text="Run Phase 1: Maklumat Am",
            command=self.run_automation_phase1_only,
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 2: Bahagian A",
            command=self.run_automation_phase2_only,
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 3: Lampiran",
            command=self.run_automation_phase3_only,
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 4: Perakuan",
            command=self.run_automation_phase4_only,
        ).pack(pady=5, fill="x")

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=20)

        bottom_button_frame = ttk.Frame(main_frame)
        bottom_button_frame.pack(fill="x", pady=10)

        ttk.Button(
            bottom_button_frame,
            text="Run Full Automation (All Steps)",
            style="Success.TButton",
            command=self.app.start_full_automation,
        ).pack(side="left", expand=True, fill="x", ipady=10, padx=(0, 5))

        ttk.Button(
            bottom_button_frame,
            text="Stop Automation",
            style="Danger.TButton",
            command=self.app.stop_automation,
        ).pack(side="left", expand=True, fill="x", ipady=10, padx=(5, 0))

        log_frame = ttk.LabelFrame(main_frame, text="Automation Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.log_area = scrolledtext.ScrolledText(
            log_frame, wrap="word", height=10, state="disabled", font=("Consolas", 9)
        )
        self.log_area.pack(fill="both", expand=True)

    def run_automation_phase1_only(self):
        self.start_automation_thread(
            self.app.automation_instance.run_phase_1,
            "Starting Phase 1: Maklumat Am...",
            "Phase 1 completed successfully.",
        )

    def run_automation_phase2_only(self):
        company_data = self.get_company_data_from_form()
        insurance_data = self.get_insurance_data_from_form()
        if company_data and insurance_data:
            self.start_automation_thread(
                self.app.automation_instance.run_phase_2_bahagian_a,
                "Starting Phase 2: Bahagian A...",
                "Phase 2 completed successfully.",
                company_data,
                insurance_data,
            )

    def run_automation_phase3_only(self):
        if not self.app.automation_instance:
            messagebox.showerror(
                "Error", "Chrome is not prepared. Please connect first."
            )
            return

        threading.Thread(target=self._threaded_phase3_runner, daemon=True).start()

    def _threaded_phase3_runner(self):
        self.log_message("Starting Phase 3: Lampiran...")
        self.app.update_status("Running Phase 3...", "#17a2b8")

        try:
            company_data = self.get_company_data_from_form()
            source_pdf = self.app.uploaded_pdf_path
            unique_id = self.app.adjudikasi_id.get()
            old_roc = company_data.get("old_roc") if company_data else None
            new_roc = company_data.get("new_roc") if company_data else None

            if not all([company_data, source_pdf, unique_id, old_roc, new_roc]):
                error_msg = "Please ensure a Source PDF is uploaded and the Adjudication Number, Old ROC, and New ROC fields are all filled."
                self.log_message(f"ERROR: {error_msg}")
                self.app.after(
                    0, messagebox.showerror, "Missing Information", error_msg
                )
                return

            self.log_message("Creating Labeled PDF...")
            roc_text = f"{new_roc}/{old_roc}"
            pdf_filename = os.path.basename(source_pdf)
            output_folder = self.app.export_dir_var.get()
            labeled_pdf_path = os.path.join(output_folder, pdf_filename)
            os.makedirs(output_folder, exist_ok=True)

            if not pdf_processor.add_labels_to_pdf(
                source_pdf, labeled_pdf_path, unique_id, roc_text
            ):
                self.log_message("ERROR: Failed to create labeled PDF.")
                self.app.after(
                    0, messagebox.showerror, "Error", "Failed to create labeled PDF."
                )
                return

            self.log_message(f"Labeled PDF created at: {labeled_pdf_path}")

            self.app.automation_instance.run_phase_3_lampiran(labeled_pdf_path)
            self.log_message("SUCCESS: Phase 3 completed successfully.")
            self.app.after(
                0, messagebox.showinfo, "Success", "Phase 3 completed successfully."
            )

        except Exception as e:
            self._handle_error(e)  # Use the centralized error handler
        finally:
            if self.app.driver and self.app.automation_instance:
                self.app.after(
                    0, self.app.update_status, "● Connected to Chrome", "#28a745"
                )
            else:
                self.app.after(0, self.app.update_status, "● Disconnected", "#6c757d")
            self.app.stop_event.clear()

    def run_automation_phase4_only(self):
        company_name = self.app.company_name.get()
        policy_number = self.app.policy_number.get()
        if not all([company_name, policy_number]):
            messagebox.showerror(
                "Missing Information",
                "Please ensure Company Name and Policy Number are filled.",
            )
            return

        reference_text = f"{company_name} {policy_number}"
        self.start_automation_thread(
            self.app.automation_instance.run_phase_4_perakuan,
            "Starting Phase 4: Perakuan...",
            "Phase 4 completed successfully.",
            reference_text,
        )

    def _threaded_full_automation(self):
        self.log_message("Starting Full Automation...")
        try:
            company_data = self.get_company_data_from_form()
            insurance_data = self.get_insurance_data_from_form()
            if not company_data or not insurance_data or not self.app.uploaded_pdf_path:
                self.app.after(
                    0,
                    messagebox.showerror,
                    "Validation Error",
                    "Ensure Company, Insurance, and a Source PDF are all provided.",
                )
                self.log_message(
                    "ERROR: Validation failed. Check company, insurance, and PDF data."
                )
                return

            self.app.stop_event.clear()

            self.app.update_status("Running Phase 1...", "#17a2b8")
            self.log_message("Running Phase 1: Maklumat Am...")
            id_result = self.app.automation_instance.run_phase_1()

            if id_result:
                self.app.after(0, self.app.adjudikasi_id.set, id_result)

            self.app.automation_instance._check_stop_signal()
            self.log_message(f"Phase 1 completed. Adjudikasi ID: {id_result}")

            if not id_result:
                self.app.after(
                    0,
                    messagebox.showerror,
                    "Error",
                    "Could not retrieve Adjudikasi ID.",
                )
                self.log_message("ERROR: Could not retrieve Adjudikasi ID.")
                return

            self.app.update_status("Creating Labeled PDF...", "#17a2b8")
            self.log_message("Creating Labeled PDF...")
            roc_text = (
                f"{company_data.get('new_roc', '')}/{company_data.get('old_roc', '')}"
            )
            pdf_filename = os.path.basename(self.app.uploaded_pdf_path)
            output_folder = self.app.export_dir_var.get()
            labeled_pdf_path = os.path.join(output_folder, pdf_filename)
            os.makedirs(output_folder, exist_ok=True)
            if not pdf_processor.add_labels_to_pdf(
                self.app.uploaded_pdf_path, labeled_pdf_path, id_result, roc_text
            ):
                self.app.after(
                    0, messagebox.showerror, "Error", "Failed to create labeled PDF."
                )
                self.log_message("ERROR: Failed to create labeled PDF.")
                return
            self.app.automation_instance._check_stop_signal()
            self.log_message(f"Labeled PDF created at: {labeled_pdf_path}")

            self.app.update_status("Running Phase 2...", "#17a2b8")
            self.log_message("Running Phase 2: Bahagian A...")
            self.app.automation_instance.run_phase_2_bahagian_a(
                company_data, insurance_data
            )
            self.app.automation_instance._check_stop_signal()
            self.log_message("Phase 2 completed.")

            self.app.update_status("Running Phase 3...", "#17a2b8")
            self.log_message("Running Phase 3: Lampiran...")
            self.app.automation_instance.run_phase_3_lampiran(labeled_pdf_path)
            self.app.automation_instance._check_stop_signal()
            self.log_message("Phase 3 completed.")

            self.app.update_status("Running Phase 4...", "#17a2b8")
            self.log_message("Running Phase 4: Perakuan...")
            company_name = company_data.get("name", "")
            policy_number = self.app.policy_number.get()
            reference_text = f"{company_name} {policy_number}"
            self.app.automation_instance.run_phase_4_perakuan(reference_text)
            self.app.automation_instance._check_stop_signal()
            self.log_message("Phase 4 completed.")

            success_message = "Full automation completed successfully!\n\nPlease check if the data have been auto inserted correctly."
            self.app.after(
                0,
                messagebox.showinfo,
                "Success",
                success_message,
            )
            self.log_message("SUCCESS: Full automation completed!")

        except InterruptedError:
            self.log_message(
                "WARNING: Full automation process was stopped by the user."
            )
            self.app.after(
                0,
                messagebox.showwarning,
                "Automation Interrupted",
                "The full automation process was stopped by the user.",
            )
        except Exception as e:
            self._handle_error(e)  # Use the centralized error handler
        finally:
            if (
                self.app.driver
                and self.app.automation_instance
                and not self.app.stop_event.is_set()
            ):
                self.app.after(
                    0, self.app.update_status, "● Connected to Chrome", "#28a745"
                )
            else:
                self.app.after(0, self.app.update_status, "● Disconnected", "#6c757d")
            self.app.stop_event.clear()
