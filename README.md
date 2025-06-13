# IGStampingAuto

**IGStampingAuto** is a desktop application designed to automate data entry on a specific website. It streamlines the workflow by intelligently processing PDF documents, populating forms with company and insurance information, and preparing submissions for final review.

---

## Features

* **Persistent Data Storage:** Saves and manages all company and insurance company information using an **SQLite database (`data.db`)**.
* **Full CRUD Functionality:** Easily **create, read, update, and delete** records for both companies and insurance companies directly through the user interface.
* **Live Search:** Find records quickly with real-time **search dropdowns** that filter names as you type.
* **Intelligent PDF Parsing:** Extracts company names and addresses from PDF documents, even without explicit labels.
* **Smart Form Population:**
    * **Known Companies:** Populates forms from the database if an uploaded PDF contains a recognized company.
    * **New Companies:** Fills forms with data extracted directly from the PDF for new companies.
* **Automated PDF Labeling:** Generates a new PDF with **custom header labels** (like ID, ROC) before automation begins.
* **Streamlined Workflow:** Automatically **pre-fills insurance information** on startup to save time.
* **Custom UI:** Features a refined layout with **color-coded buttons** for key actions, enhancing usability.

---

## Project Structure

```
IGStampingAuto/
├── .gitignore             # Files and directories to be ignored by Git
├── .flake8                # Configuration for the Flake8 linter
├── requirements.txt       # Lists all Python package dependencies
│
├── main.py                # Main application file (UI and core logic)
├── database.py            # Handles all SQLite database operations
├── pdf_processor.py       # Manages all PDF reading, parsing, and writing
│
├── data.db                # The SQLite database file (automatically created on first run)
├── venv/                  # Python virtual environment (isolated dependencies)
└── chromedriver.exe       # WebDriver for Selenium to control Google Chrome
```

---

## Developer Setup Guide

### Prerequisites

Ensure you have these installed:

* **Python 3.10+**
* **Google Chrome** browser
* **Git** (Download from [git-scm.com](https://git-scm.com/))

### Step-by-Step Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd IGStampingAuto
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate the virtual environment (for Windows PowerShell)
    .\venv\Scripts\Activate.ps1
    # For macOS/Linux or Windows Command Prompt, use: source venv/bin/activate
    ```

3.  **Install Required Packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download ChromeDriver:**
    * Visit the [Chrome for Testing repository](https://googlechromelabs.github.io/chrome-for-testing/) to download the **ChromeDriver version that exactly matches your installed Google Chrome browser**.
    * **Unzip** the downloaded file and place `chromedriver.exe` directly into the root `IGStampingAuto` project folder.

---

## Running the Application

Once your virtual environment is active and ChromeDriver is in place, you can launch the application:

```bash
python main.py
```

---