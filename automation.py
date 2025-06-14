from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,  # Re-added this import, as it's useful for debugging click issues
)


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

    def _fill_party_details(self, party_data):
        """
        A helper function to fill the details form in the popup.
        This avoids code duplication for Pihak A and Pihak B.
        """
        try:
            # 1. Wait for the popup/modal to become visible first
            print("Waiting for the popup modal to appear...")
            modal_locator = (By.CSS_SELECTOR, "div.bootbox")
            self.wait.until(EC.visibility_of_element_located(modal_locator))
            print("Popup modal is visible.")

            # 2. Now, wait for the iframe to be present and switch to it
            print("Waiting to locate the popup iframe and switch to it.")
            iframe_locator = (By.XPATH, "//iframe[contains(@src, 'popup_ssm.cfm')]")
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(iframe_locator))
            print("Successfully switched to popup iframe.")

            # --- IMPROVED WAITING STRATEGY FOR FORM FIELDS ---
            # Wait for the first field to be clickable (visible and enabled)
            name_field_locator = (By.NAME, "tb_nama_syarikat")
            print("Waiting for form fields to become interactive inside iframe...")
            name_field = self.wait.until(EC.element_to_be_clickable(name_field_locator))
            print("Form fields are ready. Filling details...")

            # Now that the form is ready, send all data
            name_field.send_keys(party_data.get("name", ""))
            self.driver.find_element(By.NAME, "tb_roc_lama").send_keys(
                party_data.get("old_roc", "")
            )
            self.driver.find_element(By.NAME, "tb_roc_new").send_keys(
                party_data.get("new_roc", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat1").send_keys(
                party_data.get("address_1", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat2").send_keys(
                party_data.get("address_2", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat3").send_keys(
                party_data.get("address_3", "")
            )
            self.driver.find_element(By.NAME, "tb_bandar").send_keys(
                party_data.get("city", "")
            )
            self.driver.find_element(By.NAME, "tb_poskod").send_keys(
                party_data.get("postcode", "")
            )

            # For the state dropdown, ensure it's visible before selecting
            state_dropdown = self.wait.until(
                EC.visibility_of_element_located((By.NAME, "id_negeri"))
            )
            Select(state_dropdown).select_by_visible_text(
                party_data.get("state", "").upper()
            )

            self.driver.find_element(By.NAME, "tb_telefon").send_keys(
                party_data.get("phone", "")
            )
            print(f"All fields filled for '{party_data.get('name')}'.")

            # Click the 'Simpan' (Save) button
            simpan_button_locator = (
                By.CSS_SELECTOR,
                "div.bootbox div.button > input[type='button'][value='Simpan']",
            )
            self.wait.until(EC.element_to_be_clickable(simpan_button_locator)).click()
            print("Clicked 'Simpan'.")

            # After clicking simpan, there might be another small confirmation popup
            ok_button_after_save_locator = (By.CSS_SELECTOR, "div.bootbox button")
            self.wait.until(
                EC.element_to_be_clickable(ok_button_after_save_locator)
            ).click()
            print("Clicked 'OK' on confirmation popup.")

        except TimeoutException as te:
            print(f"Timeout error in _fill_party_details: {te}")
            raise  # Re-raise to be caught by run_phase_2_bahagian_a
        except NoSuchElementException as nse:
            print(f"Element not found in _fill_party_details: {nse}")
            raise
        except ElementClickInterceptedException as ecie:  # Catch this specific error
            print(
                f"Click intercepted in _fill_party_details: {ecie}. Another element might be covering the target."
            )
            raise
        except Exception as e:
            print(f"An unexpected error occurred in _fill_party_details: {e}")
            raise
        finally:
            # Always switch back to the main document context
            self.driver.switch_to.default_content()
            print("Switched back to main document.")

    def run_phase_1(self):
        """
        Completes the first page of the form to get the Adjudikasi Number.
        """
        print("--- Running Phase 1: Maklumat Am ---")
        try:
            self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Permohonan Baru"))
            ).click()
            print("Clicked 'Permohonan Baru'.")

            # Wait for the dropdowns to be visible before interacting
            instrument_dropdown = self.wait.until(
                EC.visibility_of_element_located((By.ID, "id_kod_instrumen"))
            )
            Select(instrument_dropdown).select_by_value("0028/0029")
            print("Selected 'BON JAMINAN/PERJANJIAN INDEMNITI'.")

            jenis_instrument_dropdown = self.wait.until(
                EC.visibility_of_element_located((By.ID, "id_kod_jenis_instrumen"))
            )
            Select(jenis_instrument_dropdown).select_by_visible_text("Bon Jaminan Am")
            print("Selected 'Bon Jaminan Am'.")

            self.wait.until(
                EC.element_to_be_clickable((By.NAME, "btn_seterusnya"))
            ).click()
            print("Clicked 'Seterusnya' button.")

            adjudikasi_element = self.wait.until(
                EC.visibility_of_element_located((By.ID, "adjudikasi"))
            )
            adjudikasi_id = adjudikasi_element.text
            print(f"Successfully fetched Nombor Adjudikasi: {adjudikasi_id}")
            return adjudikasi_id
        except Exception as e:
            print(f"An error occurred in Phase 1: {e}")
            raise

    def run_phase_2_bahagian_a(self, company_data, insurance_data):
        """
        Completes 'Bahagian A' for both the company (Pihak A) and the insurance company (Pihak B).
        """
        print("--- Running Phase 2: Bahagian A ---")
        try:
            # 1. Switch to the Bahagian A tab
            bahagian_a_tab_locator = (By.XPATH, "//a[@href='#bhgn-a']")
            self.wait.until(EC.element_to_be_clickable(bahagian_a_tab_locator)).click()
            print("Switched to Bahagian A tab.")

            # --- Pihak A (Main Company) ---
            pihak_a_button_locator = (
                By.XPATH,
                "//*[@id='bhgn-a']/div/div[1]/div[2]/p/a[2]",
            )
            print("Waiting for Pihak A button to be clickable...")
            self.wait.until(EC.element_to_be_clickable(pihak_a_button_locator)).click()
            print("Clicked link to add Pihak A (Company)...")

            self._fill_party_details(company_data)
            print("Finished filling details for Pihak A.")

            # --- Pihak B (Insurance Company) ---
            pihak_b_button_locator = (
                By.XPATH,
                "//*[@id='bhgn-a']/div/div[2]/div[2]/p/a[2]",
            )
            print("Waiting for Pihak B button to be clickable...")
            self.wait.until(EC.element_to_be_clickable(pihak_b_button_locator)).click()
            print("Clicked link to add Pihak B (Insurance)...")

            self._fill_party_details(insurance_data)
            print("Finished filling details for Pihak B.")

            print("Successfully completed Phase 2 for both parties.")

        except Exception as e:
            print(f"An error occurred in Phase 2: {e}")
            try:
                self.driver.switch_to.default_content()
            except Exception as se:
                print(f"Error switching back to default content: {se}")
            raise

    def run_phase_3_bahagian_b(self):
        print("--- Running Phase 3: Bahagian B ---")
        # Placeholder for future implementation

    def run_phase_4_lampiran(self, path_to_labeled_pdf):
        """
        Handles the file upload in the 'Lampiran' section.
        """
        print("--- Running Phase 4: Lampiran ---")
        try:
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='#lampiran']"))
            ).click()
            print("Switched to Lampiran tab.")

            file_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "fail_lampiran"))
            )
            file_input.send_keys(path_to_labeled_pdf)
            print(f"Successfully sent PDF path to file input: {path_to_labeled_pdf}")

            self.wait.until(EC.element_to_be_clickable((By.ID, "btn_lampiran"))).click()
            print("Clicked 'Muatnaik' (Upload) button.")
        except Exception as e:
            print(f"An error occurred in Phase 4: {e}")
            raise

    def run_phase_5_perakuan(self):
        print("--- Running Phase 5: Perakuan ---")
        # Placeholder for future implementation
