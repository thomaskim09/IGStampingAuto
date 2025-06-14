# automation.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

    def run_phase_2_bahagian_a(self, company_data):
        """
        Completes the 'Bahagian A' section of the form using provided data.
        """
        print("--- Running Phase 2: Bahagian A ---")
        try:
            # 1. Switch to the Bahagian A tab
            print("Switching to Bahagian A tab...")
            bahagian_a_tab_locator = (By.XPATH, "//a[@href='#bhgn-a']")
            bahagian_a_tab = self.wait.until(
                EC.element_to_be_clickable(bahagian_a_tab_locator)
            )
            bahagian_a_tab.click()

            # 2. Click the link to open the company pop-up
            print("Clicking 'Syarikat Berdaftar Dengan SSM' link...")
            ssm_link_locator = (By.PARTIAL_LINK_TEXT, "Syarikat Berdaftar Dengan SSM")
            ssm_link = self.wait.until(EC.element_to_be_clickable(ssm_link_locator))
            ssm_link.click()

            # --- Handle the Pop-up (Facebox) ---
            # Facebox often uses an iframe. We must switch to it first.
            # If this fails, the popup might not be in an iframe.
            try:
                # TODO: Right-click in the popup and 'Inspect'. Look for an <iframe> tag.
                # Get its 'id' or 'name' attribute and put it here.
                iframe_locator = (By.TAG_NAME, "iframe")  # A common guess
                self.wait.until(
                    EC.frame_to_be_available_and_switch_to_it(iframe_locator)
                )
                print("Successfully switched to popup iframe.")
            except TimeoutException:
                print(
                    "Could not find an iframe. Assuming popup is in the main document."
                )

            # 3. Fill Company Name
            name_field_locator = (By.NAME, "tb_nama")
            name_field = self.wait.until(
                EC.visibility_of_element_located(name_field_locator)
            )
            name_field.send_keys(company_data.get("name", ""))

            # 4. Select 'Sendirian Berhad'
            jenis_dropdown = Select(
                self.driver.find_element(By.NAME, "jenis_perniagaan")
            )
            jenis_dropdown.select_by_visible_text("Sendirian Berhad / Sdn Bhd")

            # 5. Fill ROC numbers
            self.driver.find_element(By.ID, "tb_roc").send_keys(
                company_data.get("old_roc", "")
            )
            self.driver.find_element(By.ID, "tb_roc_new").send_keys(
                company_data.get("new_roc", "")
            )

            # 6. Select 'Tempatan'
            Select(
                self.driver.find_element(By.NAME, "tb_syarikat")
            ).select_by_visible_text("Tempatan")

            # 7. Fill address fields
            self.driver.find_element(By.NAME, "tb_alamat_1").send_keys(
                company_data.get("address_1", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat_2").send_keys(
                company_data.get("address_2", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat_3").send_keys(
                company_data.get("address_3", "")
            )
            self.driver.find_element(By.NAME, "tb_city").send_keys(
                company_data.get("city", "")
            )
            self.driver.find_element(By.NAME, "tb_poskod").send_keys(
                company_data.get("postcode", "")
            )

            # 8. Select State
            Select(self.driver.find_element(By.ID, "negeri1")).select_by_visible_text(
                company_data.get("state", "")
            )

            # 9. Fill Phone Number
            self.driver.find_element(By.NAME, "tb_telno").send_keys(
                company_data.get("phone", "")
            )
            print("All fields in popup filled.")

            # 10. Click 'Simpan'
            simpan_button_locator = (
                By.CSS_SELECTOR,
                "input.btn-primary[value='Simpan ']",
            )
            simpan_button = self.wait.until(
                EC.element_to_be_clickable(simpan_button_locator)
            )
            simpan_button.click()
            print("Clicked 'Simpan'.")

            # After submitting, switch back to the main content
            self.driver.switch_to.default_content()
            print("Switched back to main document.")

        except Exception as e:
            print(f"An error occurred in Phase 2: {e}")
            # Ensure we switch back even if there's an error
            self.driver.switch_to.default_content()

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
