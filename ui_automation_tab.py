# ui_automation_tab.py

from tkinter import ttk, messagebox
import os
import threading
import pdf_processor


class AutomationTab:
    def __init__(self, parent_tab, app):
        self.parent_tab = parent_tab
        self.app = app
        self.create_widgets()

    def get_company_data_from_form(self):
        # This method is unchanged
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
        # This method is unchanged
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

    def _threaded_automation_runner(self, task_function, success_message, *args):
        """
        A generic wrapper to run any automation task in a background thread.
        """
        try:
            task_function(*args)
            # Schedule success message to run on main thread
            self.app.after(0, messagebox.showinfo, "Success", success_message)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            # Schedule error message to run on main thread
            self.app.after(0, messagebox.showerror, "Automation Error", error_message)
        finally:
            # Always reset status bar on main thread after task completion
            if self.app.driver and self.app.automation_instance:
                self.app.after(
                    0, self.app.update_status, "● Connected to Chrome", "#28a745"
                )
            else:
                self.app.after(0, self.app.update_status, "● Disconnected", "#6c757d")

    def start_automation_thread(
        self, task_function, status_text, success_message, *args
    ):
        """
        Validates connection and starts the threaded automation runner.
        """
        if not self.app.automation_instance:
            messagebox.showerror(
                "Error", "Chrome is not prepared. Please connect first."
            )
            return

        self.app.update_status(status_text, "#17a2b8")  # Blue for "Running"
        threading.Thread(
            target=self._threaded_automation_runner,
            args=(task_function, success_message, *args),
            daemon=True,
        ).start()

    def create_widgets(self):
        """Creates and arranges all widgets in the automation tab."""
        main_frame = ttk.Frame(self.parent_tab, padding=20)
        main_frame.pack(expand=True, fill="both")

        # Each button now calls 'start_automation_thread' with its specific task and messages
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
            text="Run Phase 3: Bahagian B",
            command=self.run_automation_phase3_only,
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 4: Lampiran",
            command=self.run_automation_phase4_only,
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 5: Perakuan",
            command=self.run_automation_phase5_only,
        ).pack(pady=5, fill="x")

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=20)

        ttk.Button(
            main_frame,
            text="Run Full Automation (All Steps)",
            style="Success.TButton",
            command=self.start_full_automation,
        ).pack(pady=10, fill="x", ipady=10)

    def run_automation_phase1_only(self):
        self.start_automation_thread(
            self.app.automation_instance.run_phase_1,
            "Running Phase 1: Maklumat Am...",
            "Phase 1 completed successfully.",
        )

    def run_automation_phase2_only(self):
        company_data = self.get_company_data_from_form()
        insurance_data = self.get_insurance_data_from_form()
        if company_data and insurance_data:
            self.start_automation_thread(
                self.app.automation_instance.run_phase_2_bahagian_a,
                "Running Phase 2: Bahagian A...",
                "Phase 2 completed successfully.",
                company_data,
                insurance_data,
            )

    def run_automation_phase3_only(self):
        self.start_automation_thread(
            self.app.automation_instance.run_phase_3_bahagian_b,
            "Running Phase 3: Bahagian B...",
            "Phase 3 completed successfully.",
        )

    def run_automation_phase4_only(self):
        # Phase 4 requires the labeled PDF path, which is only generated in the full flow
        messagebox.showinfo(
            "Info", "Phase 4 can only be run as part of the 'Full Automation' process."
        )

    def run_automation_phase5_only(self):
        self.start_automation_thread(
            self.app.automation_instance.run_phase_5_perakuan,
            "Running Phase 5: Perakuan...",
            "Phase 5 completed successfully.",
        )

    def _threaded_full_automation(self):
        """The entire multi-step automation process running in a thread."""
        try:
            # --- 1. Validate data ---
            company_data = self.get_company_data_from_form()
            insurance_data = self.get_insurance_data_from_form()
            if not company_data or not insurance_data or not self.app.uploaded_pdf_path:
                self.app.after(
                    0,
                    messagebox.showerror,
                    "Validation Error",
                    "Ensure Company, Insurance, and a Source PDF are all provided.",
                )
                return

            # --- 2. Run Phase 1 ---
            self.app.update_status("Running Phase 1...", "#17a2b8")
            id_result = self.app.automation_instance.run_phase_1()
            if not id_result:
                self.app.after(
                    0,
                    messagebox.showerror,
                    "Error",
                    "Could not retrieve Adjudikasi ID.",
                )
                return
            self.app.adjudikasi_id.set(id_result)

            # --- 3. Create Labeled PDF ---
            self.app.update_status("Creating Labeled PDF...", "#17a2b8")
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
                return

            # --- 4. Run remaining phases ---
            self.app.update_status("Running Phase 2...", "#17a2b8")
            self.app.automation_instance.run_phase_2_bahagian_a(
                company_data, insurance_data
            )
            self.app.update_status("Running Phase 3...", "#17a2b8")
            self.app.automation_instance.run_phase_3_bahagian_b()
            self.app.update_status("Running Phase 4...", "#17a2b8")
            self.app.automation_instance.run_phase_4_lampiran(labeled_pdf_path)
            self.app.update_status("Running Phase 5...", "#17a2b8")
            self.app.automation_instance.run_phase_5_perakuan()

            self.app.after(
                0,
                messagebox.showinfo,
                "Success",
                "Full automation completed successfully!",
            )

        except Exception as e:
            error_message = f"An error occurred during full automation: {str(e)}"
            print(error_message)
            self.app.after(0, messagebox.showerror, "Automation Error", error_message)
        finally:
            if self.app.driver and self.app.automation_instance:
                self.app.after(
                    0, self.app.update_status, "● Connected to Chrome", "#28a745"
                )
            else:
                self.app.after(0, self.app.update_status, "● Disconnected", "#6c757d")

    def start_full_automation(self):
        if not self.app.automation_instance:
            messagebox.showerror("Error", "Chrome is not prepared.")
            return
        threading.Thread(target=self._threaded_full_automation, daemon=True).start()
