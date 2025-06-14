from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import threading


class StampsAutomation:
    """
    Handles all Selenium browser automation steps for the STAMPS website.
    """

    def __init__(
        self, driver, stop_event: threading.Event, log_callback=None
    ):  # Accept log_callback
        """
        Initializes the automation class with a Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 5)  # 5-second wait timeout
        self.stop_event = stop_event
        self.log_callback = (
            log_callback if log_callback else print
        )  # Store callback, default to print

    def _log(self, message):
        """Helper to send messages to the UI log or console."""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)  # Fallback to print if no callback is set

    def _check_stop_signal(self):
        """Checks if the stop event is set and raises an exception if it is."""
        if self.stop_event.is_set():
            self._log("Automation stop signal detected.")  # Log the signal
            raise InterruptedError("Automation stopped by user.")

    def _fill_party_details(self, party_data, expected_modal_title):
        """
        Helper function to fill the details form.
        It now waits for the internal TIN/ROC lookup to complete before submitting.
        """
        self._check_stop_signal()
        try:
            self._log("Waiting for the popup modal to appear...")
            modal_locator = (By.CSS_SELECTOR, "div.bootbox.modal.fade.in")
            self.wait.until(EC.visibility_of_element_located(modal_locator))
            self._log("Popup modal is visible.")

            self.wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        f"//h4[@class='modal-title']/span[contains(text(), '{expected_modal_title}')]",
                    )
                )
            )
            self._log(f"Modal with title '{expected_modal_title}' is visible.")

            # --- Fill form fields BEFORE the AJAX trigger ---
            self.wait.until(EC.element_to_be_clickable((By.NAME, "tb_nama"))).send_keys(
                party_data.get("name", "")
            )
            Select(
                self.wait.until(
                    EC.visibility_of_element_located((By.ID, "jenis_perniagaan"))
                )
            ).select_by_value(party_data.get("business_type", ""))
            Select(
                self.wait.until(
                    EC.visibility_of_element_located((By.NAME, "tb_syarikat"))
                )
            ).select_by_value("1")

            # --- Fill the Old ROC field ---
            old_roc_field = self.driver.find_element(By.NAME, "tb_roc")
            old_roc_field.send_keys(party_data.get("old_roc", ""))
            self._log(f"Filled Old ROC with: {party_data.get('old_roc')}")

            # This triggers the onchange/onblur event and starts the TIN lookup.
            self._log("Simulating TAB press to trigger TIN lookup...")
            old_roc_field.send_keys(Keys.TAB)

            # --- Now, wait for the TIN lookup to complete ---
            self._log("Waiting for the TIN lookup to complete...")
            nota_locator = (
                By.XPATH,
                "//*[@id='label_awamberhad' or @id='label_tin500']",
            )
            self.wait.until(EC.visibility_of_element_located(nota_locator))
            self._log("TIN lookup complete. 'Nota' label is visible.")

            # --- Now that the modal is stable, fill the REMAINING fields ---
            self._log("Proceeding to fill remaining fields...")
            self.driver.find_element(By.NAME, "tb_roc_new").send_keys(
                party_data.get("new_roc", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat_1").send_keys(
                party_data.get("address_1", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat_2").send_keys(
                party_data.get("address_2", "")
            )
            self.driver.find_element(By.NAME, "tb_alamat_3").send_keys(
                party_data.get("address_3", "")
            )
            self.driver.find_element(By.NAME, "tb_city").send_keys(
                party_data.get("city", "")
            )
            self.driver.find_element(By.NAME, "tb_poskod").send_keys(
                party_data.get("postcode", "")
            )
            Select(
                self.wait.until(EC.visibility_of_element_located((By.NAME, "negeri1")))
            ).select_by_visible_text(party_data.get("state", ""))
            self.driver.find_element(By.NAME, "tb_telno").send_keys(
                party_data.get("phone", "")
            )
            self._log(f"All fields filled for '{party_data.get('name')}'.")

            # --- Finally, click the 'Simpan' button using the robust JavaScript method ---
            form_id = ""
            if "Tambah Pemberi/Penjual" in expected_modal_title:
                form_id = "add-penjual-com"
                # The Pihak A button works, so we can click it normally
                self._log("Pihak A form: Using JavaScript click on 'Simpan' button.")
                simpan_button_locator = (
                    By.CSS_SELECTOR,
                    f"form#{form_id} input[type='submit'][value='Simpan ']",
                )
                simpan_button_element = self.wait.until(
                    EC.presence_of_element_located(simpan_button_locator)
                )
                self.driver.execute_script(
                    "arguments[0].click();", simpan_button_element
                )

            elif "Tambah Penerima/Pembeli" in expected_modal_title:
                form_id = "add-pembeli-com"
                # The Pihak B button is broken. We find the form and submit it directly.
                self._log(
                    "Pihak B form: Bypassing broken button and submitting the form directly."
                )
                form_element = self.driver.find_element(By.ID, form_id)
                form_element.submit()

            self._log("Form submission command has been sent.")

        except Exception as e:
            self._log(
                f"ERROR: An unexpected error occurred in _fill_party_details: {e}"
            )
            raise

    def run_phase_1(self):
        self._check_stop_signal()
        self._log("--- Running Phase 1: Maklumat Am ---")
        try:
            self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Permohonan Baru"))
            ).click()
            self._check_stop_signal()
            self._log("Clicked 'Permohonan Baru'.")

            instrument_dropdown = self.wait.until(
                EC.visibility_of_element_located((By.ID, "id_kod_instrumen"))
            )
            Select(instrument_dropdown).select_by_value("0028/0029")
            self._check_stop_signal()
            self._log("Selected 'BON JAMINAN/PERJANJIAN INDEMNITI'.")

            jenis_instrument_dropdown = self.wait.until(
                EC.visibility_of_element_located((By.ID, "id_kod_jenis_instrumen"))
            )
            Select(jenis_instrument_dropdown).select_by_visible_text("Bon Jaminan Am")
            self._check_stop_signal()
            self._log("Selected 'Bon Jaminan Am'.")

            self.wait.until(
                EC.element_to_be_clickable((By.NAME, "btn_seterusnya"))
            ).click()
            self._check_stop_signal()
            self._log("Clicked 'Seterusnya' button.")

            adjudikasi_element = self.wait.until(
                EC.visibility_of_element_located((By.ID, "adjudikasi"))
            )
            adjudikasi_id = adjudikasi_element.text
            self._check_stop_signal()
            self._log(f"Successfully fetched Nombor Adjudikasi: {adjudikasi_id}")
            return adjudikasi_id
        except InterruptedError:
            self._log("Automation interrupted by user in Phase 1.")
            raise
        except Exception as e:
            self._log(f"ERROR: An error occurred in Phase 1: {e}")
            raise

    def run_phase_2_bahagian_a(self, company_data, insurance_data):
        self._check_stop_signal()
        self._log("--- Running Phase 2: Bahagian A ---")
        try:
            # --- Navigate to the correct tab ---
            bahagian_a_tab_locator = (By.XPATH, "//a[@href='#bhgn-a']")
            self.wait.until(EC.element_to_be_clickable(bahagian_a_tab_locator)).click()
            self._check_stop_signal()
            self._log("Switched to Bahagian A tab.")

            # --- Pihak A (Insurance Company - First Modal) ---
            pihak_a_button_locator = (By.CSS_SELECTOR, "a[href*='seller_com']")
            self._log("Waiting for Pihak A button to be clickable...")
            self.wait.until(EC.element_to_be_clickable(pihak_a_button_locator)).click()
            self._log("Clicked link to add Pihak A (Insurance Company).")

            insurance_data["business_type"] = insurance_data.get("business_type", "5")
            self._fill_party_details(
                insurance_data, "Tambah Pemberi/Penjual (Syarikat Berdaftar Dengan SSM)"
            )
            self._log(
                "Submitted details for Pihak A. Now waiting for page to stabilize..."
            )

            # Step 1: Wait for the loading overlay to disappear. This is the most reliable
            # signal that the AJAX call (reloading the party list) is finished.
            overlay_locator = (By.ID, "overlay")
            self.wait.until(EC.invisibility_of_element_located(overlay_locator))
            self._log("Loading overlay has disappeared.")

            # Step 2: Wait for the modal itself to fully close and disappear from the DOM.
            modal_locator = (By.CSS_SELECTOR, "div.bootbox.modal")
            self.wait.until(EC.invisibility_of_element_located(modal_locator))
            self._log("First modal has disappeared. Page is stable.")

            # --- Pihak B (Main Company - Second Modal) ---
            pihak_b_button_locator = (By.CSS_SELECTOR, "a[href*='buyer_com']")
            self._log("Waiting for Pihak B button to be clickable...")
            self.wait.until(EC.element_to_be_clickable(pihak_b_button_locator)).click()

            self._check_stop_signal()
            self._log("Clicked link to add Pihak B (Company).")
            company_data["business_type"] = company_data.get("business_type", "4")
            self._fill_party_details(
                company_data,
                "Tambah Penerima/Pembeli (Syarikat Berdaftar Dengan SSM)",
            )
            self._log("Successfully submitted details for Pihak B.")
            self._log("Successfully completed Phase 2 for both parties.")

        except InterruptedError:
            self._log("Automation interrupted by user in Phase 2.")
            raise
        except Exception as e:
            error_message = getattr(e, "msg", str(e))
            self._log(f"ERROR: An error occurred in Phase 2: {error_message}")
            try:
                self.driver.switch_to.default_content()
            except Exception as se:
                self._log(f"ERROR: Error switching back to default content: {se}")
            raise

    def run_phase_3_bahagian_b(self):
        self._check_stop_signal()
        self._log("--- Running Phase 3: Bahagian B ---")
        try:
            # time.sleep(2) # Simulate work
            self._check_stop_signal()
            self._log("Phase 3 completed (placeholder).")
        except InterruptedError:
            self._log("Automation interrupted by user in Phase 3.")
            raise

    def run_phase_4_lampiran(self, path_to_labeled_pdf):
        self._check_stop_signal()
        self._log("--- Running Phase 4: Lampiran ---")
        try:
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='#lampiran']"))
            ).click()
            self._check_stop_signal()
            self._log("Switched to Lampiran tab.")

            file_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "fail_lampiran"))
            )
            file_input.send_keys(path_to_labeled_pdf)
            self._check_stop_signal()
            self._log(
                f"Successfully sent PDF path to file input: {path_to_labeled_pdf}"
            )

            self.wait.until(EC.element_to_be_clickable((By.ID, "btn_lampiran"))).click()
            self._check_stop_signal()
            self._log("Clicked 'Muatnaik' (Upload) button.")
        except InterruptedError:
            self._log("Automation interrupted by user in Phase 4.")
            raise
        except Exception as e:
            self._log(f"ERROR: An error occurred in Phase 4: {e}")
            raise

    def run_phase_5_perakuan(self):
        self._check_stop_signal()
        self._log("--- Running Phase 5: Perakuan ---")
        try:
            # time.sleep(2) # Simulate work
            self._check_stop_signal()
            self._log("Phase 5 completed (placeholder).")
        except InterruptedError:
            self._log("Automation interrupted by user in Phase 5.")
            raise
