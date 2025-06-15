# Project: IG Stamping Automation - Features & Specifications

## 1. Core Objective
A desktop application built with Python and Tkinter to streamline and automate the process of data entry for Insurance Guarantee (IG) documents on the STAMPS website.

## 2. Key Features

### Data Management & UI
* **Persistent SQLite Database**: All company and insurance provider information is stored locally in a `data.db` file for persistence.
* **Full CRUD Functionality**: The user interface provides complete Create, Read, Update, and Delete capabilities for both company and insurance records.
* **Live Search**: Dropdown search bars on both the Company and Insurance tabs filter records in real-time as the user types.
* **Pre-loaded Data**: The application automatically pre-loads an initial set of company and insurance data from JSON files on first run if the database is empty.

### Intelligent PDF Processing
* **Automated Data Extraction**: When a user uploads an IG PDF, the application automatically reads the document and extracts key information using regular expressions, including:
    * Company Name
    * Company Address
    * Policy Number
* **Smart Form Population**: The UI forms are automatically populated based on the extracted PDF data. If a matching company is found in the database, the complete record is used.

### Web Automation (Selenium)
* **End-to-End Automation**: The application can run a full, multi-step automation process that populates all necessary forms on the STAMPS website.
* **Modular Phase Execution**: Users can choose to run individual phases of the automation process (Maklumat Am, Bahagian A, Lampiran, Perakuan) independently from the "Automation Steps" tab.
* **Automated PDF Labeling**: Before the upload phase, the application programmatically generates a new PDF with the official Adjudication Number and company ROC number stamped as a header.
* **Browser Management**: Includes features to prepare, connect to, and check the status of a remote-controlled Chrome instance, guided by a multi-step instructional popup.

## 3. System Requirements
* **Operating System**: Windows
* **Browser**: Google Chrome must be installed.