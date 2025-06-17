import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config_manager


class AdvancedTab:
    """
    Manages the 'Advanced' tab UI and logic, including Chrome path configuration.
    """

    def __init__(self, parent_tab, app):
        """
        Initializes the AdvancedTab.
        'app' is a reference to the main IGStampingAuto instance.
        """
        self.parent_tab = parent_tab
        self.app = app  # Store the reference to the main app
        self.create_widgets()
        self.load_settings()  # Load settings when the tab is created

    def create_widgets(self):
        """Creates the widgets for the advanced settings tab."""
        main_frame = ttk.Frame(self.parent_tab, padding=20)
        main_frame.pack(expand=True, fill="both")

        chrome_frame = ttk.LabelFrame(
            main_frame, text="Chrome Browser Path", padding=10
        )
        chrome_frame.pack(fill="x", padx=5, pady=5)
        chrome_frame.columnconfigure(1, weight=1)

        ttk.Label(chrome_frame, text="Chrome.exe Path:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )

        self.chrome_path_var = tk.StringVar()
        ttk.Entry(
            chrome_frame, textvariable=self.chrome_path_var, state="readonly"
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            chrome_frame, text="Browse...", command=self.browse_chrome_path
        ).grid(row=0, column=2, sticky="e", padx=5, pady=5)

        ttk.Button(
            chrome_frame,
            text="Save Settings",
            style="Success.TButton",
            command=self.save_settings,
        ).grid(row=1, column=2, sticky="e", padx=(5, 5), pady=(10, 5))

    def browse_chrome_path(self):
        """Opens a file dialog to select the chrome.exe file."""
        filetypes = [("Executable", "*.exe"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(
            title="Select Chrome Executable", filetypes=filetypes
        )
        if filepath:
            self.chrome_path_var.set(filepath)

    def save_settings(self):
        """Saves the currently selected path to the config file."""
        config = config_manager.load_config()
        config["chrome_path"] = self.chrome_path_var.get()
        config_manager.save_config(config)
        messagebox.showinfo("Success", "Settings saved successfully!")
        # Update the path on the main app instance immediately
        self.app.chrome_executable_path = self.chrome_path_var.get()

    def load_settings(self):
        """Loads the saved Chrome path from the config file on startup."""
        config = config_manager.load_config()
        chrome_path = config.get("chrome_path", "")
        self.chrome_path_var.set(chrome_path)
        # Set the path on the main app instance so other tabs can use it
        self.app.chrome_executable_path = chrome_path
