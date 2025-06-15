# IG Stamping Automation

IG Stamping Automation is a user-friendly desktop application designed to automate the repetitive and time-consuming task of data entry for Insurance Guarantee documents on the Malaysian STAMPS website. It intelligently processes PDF documents, manages company data, and controls a web browser to fill out complex forms, significantly improving workflow efficiency.

## Features

* **Intelligent PDF Parsing**: Automatically extracts company name, address, and policy number from uploaded IG documents.
* **Centralized Data Management**: Uses a local SQLite database to save and manage company and insurance provider information with full CRUD functionality.
* **End-to-End Web Automation**: Automates the entire submission process across four key phases: Maklumat Am, Bahagian A, Lampiran, and Perakuan.
* **Modular Control**: Allows users to run the full automation from start to finish or execute individual phases on demand.
* **Automated PDF Remarking**: Programmatically stamps the required Adjudication and ROC numbers onto the PDF before uploading.
* **User-Friendly Interface**: A clean, multi-tabbed GUI built with Tkinter, featuring live search, tooltips, and guided setup instructions.

## Getting Started (For Developers)

Follow these steps to set up the project for development.

### Prerequisites

* Python 3.10+
* Git

### Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd IGStampingAuto
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it (Windows)
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    python main.py
    ```

## Deployment (Creating the .exe)

The application is configured to be packaged into a single executable file using PyInstaller.

1.  **Code Preparation**: The project code includes a helper function (`resource_path`) to ensure that data files (images, JSON) are correctly found when running from the bundled `.exe`.

2.  **Run the PyInstaller Command**: From the project's root directory (with your virtual environment active), run the following command. Using `python -m PyInstaller` is recommended to avoid path issues on Windows.

    ```bash
    python -m PyInstaller --onefile --windowed --name "IGStampingAuto" --icon="resource/app_icon.png" --add-data "resource;resource" --add-data "initial_data;initial_data" main.py
    ```

3.  **Find Your Executable**: After the process completes, your standalone application (`main.exe`) will be located in the `dist` folder.

## User Guide & Testing

Here’s how to use and test the features of the application.

### Initial Setup

1.  **Run the application** (`main.exe` or `python main.py`).
2.  Click the **Prepare Chrome** button. A new Chrome window, controlled by the application, will open.
3.  An instructional popup will appear. Follow the **multi-step guide** to log into your STAMPS account and navigate to the correct starting page for a new submission.

### Testing Features

#### Company Information Tab

This is the main control center for starting a new task.

1.  **Upload PDF**: Click **Upload...** and select an Insurance Guarantee (IG) PDF.
2.  **Verify Data Extraction**: Check that the **Company Name**, **Policy Number**, and other details are automatically filled in the form fields.
3.  **Search Company**: Use the **Search Company** dropdown to find and load data for a company already saved in the database.
4.  **Manage Data**: Use the **Save Company** and **Delete Company** buttons to manage your records.

#### Insurance Company Tab

1.  **View Records**: This tab is pre-loaded with an insurance provider on startup. You can use the **Search Company** dropdown to find others.
2.  **Manage Data**: Add, update, or delete insurance company records as needed.

#### Automation Steps Tab

This tab allows for fine-grained control over the automation process.

1.  **Prerequisites**: Ensure all required data is present on the "Company Information" tab first.
2.  **Test Individual Phases**: Click any of the "Run Phase..." buttons to test a specific part of the automation. The application will perform validation checks before starting.
3.  **Test Full Automation**: Click the green **Run Full Automation** button to execute the entire process from start to finish.
4.  **Test Stop Button**: While an automation is running, click the red **Stop Automation** button to gracefully interrupt the process.