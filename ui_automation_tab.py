# ui_automation_tab.py

from tkinter import ttk, messagebox
import os
import pdf_processor


class AutomationTab:
    def __init__(self, parent_tab, app):
        self.parent_tab = parent_tab
        self.app = app
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.parent_tab, padding=20)
        main_frame.pack(expand=True, fill="both")

        def run_step(step_function):
            if not self.app.automation_instance:
                messagebox.showerror("Error", "Chrome is not prepared.")
                return
            try:
                step_function()
            except Exception as e:
                messagebox.showerror("Automation Error", f"An error occurred: {str(e)}")

        ttk.Button(
            main_frame,
            text="Run Phase 1: Maklumat Am",
            command=lambda: run_step(self.run_automation_phase1_only),
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 2: Bahagian A",
            command=lambda: run_step(
                self.app.automation_instance.run_phase_2_bahagian_a
            ),
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 3: Bahagian B",
            command=lambda: run_step(
                self.app.automation_instance.run_phase_3_bahagian_b
            ),
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 4: Lampiran",
            command=lambda: messagebox.showinfo(
                "Info",
                "This step requires the full automation flow to get the labeled PDF path.",
            ),
        ).pack(pady=5, fill="x")
        ttk.Button(
            main_frame,
            text="Run Phase 5: Perakuan",
            command=lambda: run_step(self.app.automation_instance.run_phase_5_perakuan),
        ).pack(pady=5, fill="x")

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=20)
        ttk.Button(
            main_frame,
            text="Run Full Automation (All Steps)",
            style="Success.TButton",
            command=self.start_automation,
        ).pack(pady=10, fill="x", ipady=10)

    def run_automation_phase1_only(self):
        if not self.app.automation_instance:
            messagebox.showerror("Error", "Automation instance not ready.")
            return

        id_result = self.app.automation_instance.run_phase_1()
        if id_result:
            self.app.adjudikasi_id.set(id_result)
            messagebox.showinfo(
                "Phase 1 Complete", f"Successfully fetched Adjudikasi ID: {id_result}"
            )
        else:
            messagebox.showerror("Phase 1 Failed", "Could not retrieve Adjudikasi ID.")

    def start_automation(self):
        # --- REFINEMENT 1: Validate all inputs before starting ---
        if not self.app.automation_instance:
            messagebox.showerror(
                "Error", "Chrome is not prepared. Please click 'Prepare Chrome' first."
            )
            return
        if not self.app.uploaded_pdf_path:
            messagebox.showerror(
                "Error",
                "No source PDF has been uploaded. Please upload a PDF on the 'Company Information' tab.",
            )
            return

        # --- Step 1: Run Phase 1 to get the ID ---
        id_result = self.app.automation_instance.run_phase_1()
        if not id_result:
            messagebox.showerror(
                "Process Failed", "Could not retrieve Adjudikasi ID. Aborting."
            )
            return
        self.app.adjudikasi_id.set(id_result)
        messagebox.showinfo(
            "ID Fetched", f"Adjudikasi ID: {self.app.adjudikasi_id.get()}"
        )

        # --- Step 2: Create the labeled PDF ---
        old_roc = self.app.company_old_roc.get()
        new_roc = self.app.company_new_roc.get()
        roc_text = f"{new_roc}/{old_roc}"
        pdf_filename = os.path.basename(self.app.uploaded_pdf_path)
        output_folder = self.app.export_dir_var.get()
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, pdf_filename)

        success = pdf_processor.add_labels_to_pdf(
            source_path=self.app.uploaded_pdf_path,
            output_path=output_path,
            unique_id=self.app.adjudikasi_id.get(),
            roc_text=roc_text,
        )
        if not success:
            messagebox.showerror(
                "Process Failed", "Failed to create the labeled PDF. Aborting."
            )
            return
        messagebox.showinfo("PDF Created", "Labeled PDF created successfully!")

        # --- Step 3: Run remaining phases ---
        self.app.automation_instance.run_phase_2_bahagian_a()
        self.app.automation_instance.run_phase_3_bahagian_b()

        # --- REFINEMENT 2: Pass the labeled PDF path to the upload phase ---
        self.app.automation_instance.run_phase_4_lampiran(output_path)

        self.app.automation_instance.run_phase_5_perakuan()

        messagebox.showinfo(
            "Automation Complete", "All automation steps have been executed."
        )
