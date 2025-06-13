# Project: IG Stamping Automation - Requirements

## 1. Core Objective
To automate the process of data entry on a specific website, including intelligent PDF processing and data management.

## 2. User Interface (UI)
- A multi-tab desktop application built with Python/Tkinter.
- **Company Information Tab:**
    - A search bar with live, auto-filtering dropdown (`Combobox`) to find existing companies.
    - A form to display/edit company details (Name, Address, ROC numbers, Phone).
    - A section to select a source PDF for data extraction and processing.
    - A section to display and select the export directory for the modified PDF.
    - Action buttons with custom styling (Save: green, Delete: red).
    - Button layout: Data management buttons (Clear, Save, Delete) are aligned to the left; the primary action button (Start Automation) is aligned to the right.
- **Insurance Company Information Tab:**
    - A search bar with a live, auto-filtering dropdown.
    - A form to display/edit insurance company details.
    - On application startup, this form is automatically populated with the first available insurance company record.
    - Data management buttons (Clear, Save, Delete) aligned to the left.

## 3. Data Management (SQLite)
- A local SQLite database (`data.db`) provides persistent storage.
- Full CRUD (Create, Read, Update, Delete) functionality for both company and insurance company records.
- If the insurance company database is empty on first run, it is automatically seeded with a default record (Zurich General Insurance).

## 4. PDF Processing (PyMuPDF)
- **PDF Reading/Extraction:**
    - When a PDF is uploaded, the application intelligently extracts the company name and address from the document's paragraph text without relying on fixed labels.
    - **Workflow:**
        1. Extract company name from PDF.
        2. Search the database for this name.
        3. If a match is found, populate the form with the complete record from the database.
        4. If no match is found, populate the form with the partial data (name, address) extracted from the PDF.
- **PDF Writing/Labeling:**
    - Before starting the web automation, the application generates a new, modified PDF.
    - Three distinct labels are added to the top of the first page:
        - **Top-Left:** Custom text (e.g., "For LHDN Stamping").
        - **Top-Center:** A unique ID that will be retrieved from the website.
        - **Top-Right:** The company's ROC number.

## 5. Web Automation (Selenium - *To be implemented*)
- The "Start Automation" button will trigger the web automation script.
- The script will use the data from the UI and the path to the newly labeled PDF to perform actions on the target website.

## 6. Final Output
- The final application will be packaged into a single `.exe` executable file for Windows using PyInstaller.