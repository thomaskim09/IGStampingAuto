# IGStampingAuto

## 1. Project Objective
IGStampingAuto is a desktop application designed to automate the process of data entry on a specific website. It streamlines the workflow of filling in company information, intelligently processing PDF documents, and preparing submissions for final review.

## 2. Core Features
- **Persistent Data Storage:** Uses an SQLite database (`data.db`) to save and manage all company and insurance company information.
- **Full CRUD Functionality:** Create, Read, Update, and Delete records for both companies and insurance companies through the UI.
- **Live Search:** Each tab features a search dropdown that filters the list of names in real-time as you type.
- **Intelligent PDF Parsing:** Extracts company name and address from PDF documents even without explicit labels.
- **Smart Form Population:**
    - If an uploaded PDF contains a known company, it populates the form from the database.
    - If it's a new company, it populates the form with the extracted PDF data.
- **Automated PDF Labeling:** Before starting the automation, it generates a new PDF with three custom labels (ID, ROC, etc.) added to the header.
- **Streamlined Workflow:** Automatically pre-fills the insurance information on startup to save time.
- **Custom UI:** Features a refined layout with colored buttons for key actions.

## 3. Project Structure
IGStampingAuto/
│
├── .gitignore          # Tells Git which files to ignore
├── .flake8             # Configuration for the Flake8 linter
├── requirements.txt    # Lists all Python package dependencies
│
├── main.py             # Main application file (UI and logic)
├── database.py         # Handles all SQLite database operations
├── pdf_processor.py    # Handles all PDF reading and writing
│
├── data.db             # The SQLite database file (created on first run)
├── venv/               # Your Python virtual environment folder
└── chromedriver.exe    # The driver for Selenium to control Chrome


## 4. Developer Setup Guide

### Prerequisites
* **Python 3.10+**
* **Google Chrome**
* **Git** (Download from [git-scm.com](https://git-scm.com/))

### Step-by-Step Setup
1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd IGStampingAuto
    ```
2.  **Create and Activate Virtual Environment:**
    ```bash
    # Create
    python -m venv venv
    # Activate
    venv\Scripts\activate
    ```
3.  **Install Required Packages:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Download ChromeDriver:**
    * Download the ChromeDriver that matches your Chrome version from the [Chrome for Testing repository](https://googlechromelabs.github.io/chrome-for-testing/).
    * Unzip the file and place `chromedriver.exe` in the root of the `IGStampingAuto` project folder.

## 5. Running the Application
With your virtual environment active, run the main script:
```bash
python main.py

---

### **Part 2: GitHub Setup Guide**

Follow these steps to upload your project to a private GitHub repository.

#### **Step 1: Create `requirements.txt` and `.gitignore`**

These two files are essential for any Python project on GitHub.

1.  **Create `requirements.txt`:** This file lists the Python libraries your project needs. In your `IGStampingAuto` folder, create a new file named `requirements.txt` and paste this in:
    ```
    selenium
    pymupdf
    pyinstaller
    ```

2.  **Create `.gitignore`:** This file tells Git which files and folders to **ignore**. It's crucial for preventing sensitive data or unnecessary files from being uploaded. In your `IGStampingAuto` folder, create a new file named `.gitignore` and paste this in:
    ```
    # Virtual Environment
    venv/

    # Database file - Do not commit the data itself
    data.db

    # Python cache
    __pycache__/
    *.pyc

    # IDE/Editor specific files
    .vscode/
    .idea/

    # PyInstaller build files
    dist/
    build/
    *.spec
    ```

#### **Step 2: Create the Repository on GitHub**

1.  Go to [GitHub.com](https://github.com/) and log in.
2.  Click the **+** icon in the top-right corner and select **"New repository"**.
3.  **Repository name:** `IGStampingAuto`
4.  **Description:** (Optional) "Desktop app to automate data entry and PDF processing."
5.  Select **Private**. This is very important.
6.  **Crucially, leave all the "Initialize this repository with" checkboxes UNCHECKED.** Do not add a README, .gitignore, or license from the web interface.
7.  Click **"Create repository"**.

#### **Step 3: Upload Your Project**

On the next page, GitHub will show you some commands. We will use the ones under **"...or push an existing repository from the command line"**.

1.  Open your terminal or Command Prompt **inside your `IGStampingAuto` project folder**.
2.  Run the following commands one by one:

    ```bash
    # Initialize a new Git repository in your folder
    git init

    # Add all your project files to the staging area (respecting the .gitignore)
    git add .

    # Create your first "save point" or commit
    git commit -m "Initial commit of IG Stamping Automation app"

    # Set the default branch name to "main"
    git branch -M main

    # Link your local folder to the GitHub repository you created
    # (Replace YOUR_USERNAME with your actual GitHub username)
    git remote add origin https://github.com/YOUR_USERNAME/IGStampingAuto.git

    # Push (upload) your code to GitHub
    git push -u origin main
    ```

After the last command finishes, refresh your GitHub repository page. You will see all your files (`main.py`, `database.py`, etc.) there!