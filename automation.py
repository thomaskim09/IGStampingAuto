# automation.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


class StampsAutomation:
    """
    Handles all Selenium browser automation steps for the STAMPS website.
    """

    def __init__(self, driver):
        """
        Initializes the automation class with a Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)  # 15-second wait timeout

    def run_phase_1(self):
        """
        Completes the first page of the form to get the Adjudikasi Number.
        Returns the Adjudikasi Number as a string.
        """
        print("--- Running Phase 1: Maklumat Am ---")
        adjudikasi_id = None
        try:
            # 1. Select the "Permohonan Penyeteman" radio button
            # TODO: Find the ID, NAME, or XPATH for the radio button.
            # Use browser 'Inspect' tool. Look for <input type="radio">
            permohonan_radio_locator = (By.ID, "id_for_permohonan_radio")
            permohonan_radio = self.wait.until(
                EC.element_to_be_clickable(permohonan_radio_locator)
            )
            permohonan_radio.click()
            print("Selected 'Permohonan Penyeteman' radio button.")

            # 2. In the "Pejabat Setem" dropdown, select "Johor"
            # TODO: Find the ID or NAME for the <select> element.
            pejabat_dropdown_locator = (By.ID, "id_for_pejabat_setem_dropdown")
            pejabat_dropdown = self.wait.until(
                EC.visibility_of_element_located(pejabat_dropdown_locator)
            )
            Select(pejabat_dropdown).select_by_visible_text("Johor")
            print("Selected 'Johor' from dropdown.")

            # 3. Pick today's date from the calendar
            # TODO: Find the locator for the calendar icon/button.
            calendar_icon_locator = (By.ID, "id_for_calendar_icon")
            calendar_icon = self.wait.until(
                EC.element_to_be_clickable(calendar_icon_locator)
            )
            calendar_icon.click()

            # TODO: Find a locator for today's date in the calendar pop-up.
            # Often, this has a unique class name like 'ui-datepicker-today'.
            today_date_locator = (By.CSS_SELECTOR, "a.ui-datepicker-today")
            today_date = self.wait.until(EC.element_to_be_clickable(today_date_locator))
            today_date.click()
            print(f"Selected today's date: {datetime.now().strftime('%Y-%m-%d')}")

            # 4. Click the "Seterusnya" button
            # TODO: Find the locator for the 'Seterusnya' button.
            seterusnya_button_locator = (By.ID, "id_for_seterusnya_button")
            seterusnya_button = self.wait.until(
                EC.element_to_be_clickable(seterusnya_button_locator)
            )
            seterusnya_button.click()
            print("Clicked 'Seterusnya' button.")

            # After clicking, wait for the next page and get the ID
            print("Waiting for 'Nombor Adjudikasi' to be generated...")
            # TODO: Find the locator for the element that displays the new ID.
            adjudikasi_id_locator = (By.ID, "id_of_adjudikasi_number_display")
            id_element = self.wait.until(
                EC.visibility_of_element_located(adjudikasi_id_locator)
            )
            adjudikasi_id = id_element.text
            print(f"Successfully fetched Nombor Adjudikasi: {adjudikasi_id}")

        except Exception as e:
            print(f"An error occurred in Phase 1: {e}")
            # Consider showing a tkinter messagebox error here from main.py

        return adjudikasi_id

    def run_phase_2_bahagian_a(self):
        """
        Completes the 'Bahagian A' section of the form.
        """
        print("--- Running Phase 2: Bahagian A ---")
        try:
            # 1. Switch to the Bahagian A tab/section if necessary
            # TODO: Find the locator for the 'Bahagian A' tab and click it.
            bahagian_a_tab_locator = (By.XPATH, "//a[contains(text(), 'Bahagian A')]")
            bahagian_a_tab = self.wait.until(
                EC.element_to_be_clickable(bahagian_a_tab_locator)
            )
            bahagian_a_tab.click()
            print("Switched to Bahagian A tab.")

            # 2. Click the link to open the pop-up
            # TODO: Find the locator for the "(Syarikat Berdaftar Dengan SSM)" link.
            ssm_link_locator = (By.LINK_TEXT, "(Syarikat Berdaftar Dengan SSM)")
            ssm_link = self.wait.until(EC.element_to_be_clickable(ssm_link_locator))
            ssm_link.click()
            print("Clicked SSM link to open pop-up.")

            # TODO: Add logic to switch to the pop-up window and fill the form.
            # This will require using driver.window_handles, similar to previous examples.
            print("Placeholder: Logic for pop-up form to be added here.")

        except Exception as e:
            print(f"An error occurred in Phase 2: {e}")

    def run_phase_3_bahagian_b(self):
        print("--- Running Phase 3: Bahagian B (Placeholder) ---")

    # --- REFINED: Method now accepts the PDF path ---
    def run_phase_4_lampiran(self, path_to_labeled_pdf):
        """
        Handles the file upload in the 'Lampiran' section.
        """
        print("--- Running Phase 4: Lampiran ---")
        print(f"Attempting to upload file: {path_to_labeled_pdf}")
        try:
            # TODO: Find the locator for the file input element.
            # It might be <input type="file">. It could be hidden.
            pdf_upload_locator = (By.ID, "id_for_pdf_upload_input")

            # Use send_keys to upload the file. No click is needed.
            file_input = self.driver.find_element(*pdf_upload_locator)
            file_input.send_keys(path_to_labeled_pdf)
            print("Successfully sent PDF path to file input.")

        except Exception as e:
            print(f"An error occurred in Phase 4: {e}")

    def run_phase_5_perakuan(self):
        print("--- Running Phase 5: Perakuan (Placeholder) ---")
