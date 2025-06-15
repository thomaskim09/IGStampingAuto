import fitz  # PyMuPDF
import re


def extract_info_from_pdf(pdf_path):
    """
    Extracts company name, address, and policy number from the PDF.
    """
    extracted_data = {}
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text().replace(
                "\n", " "
            )  # Replace newlines with spaces for easier matching

        # Pattern 1: Find the company name between "As requested by of" and ", of"
        name_match = re.search(
            r"As requested by of (.*?), of", full_text, re.IGNORECASE
        )
        if name_match:
            extracted_data["name"] = name_match.group(1).strip() + " SDN. BHD."

        # Pattern 2: Find the address between ", of" and "we, Zurich"
        address_match = re.search(
            r", of (NO\..*?) we, Zurich", full_text, re.IGNORECASE
        )
        if address_match:
            extracted_data["address"] = address_match.group(1).strip()

        # New Pattern 3: Find the Policy Number
        policy_match = re.search(
            r"RE: OUR REFERENCE GUARANTEE NO:\s*([\d\*-]+)", full_text, re.IGNORECASE
        )
        if policy_match:
            extracted_data["policy_number"] = policy_match.group(1).strip()

        doc.close()
        return extracted_data

    except Exception as e:
        print(f"Error processing PDF file {pdf_path}: {e}")
        return {}


def add_labels_to_pdf(source_path, output_path, unique_id, roc_text):
    """
    Adds two labels to the top of the first page of a PDF document.

    Args:
        source_path (str): The path to the original PDF.
        output_path (str): The path to save the modified PDF.
        unique_id (str): The ID from the website, to be placed in the center.
        roc_text (str): The combined ROC numbers, to be placed on the right.
    """
    try:
        doc = fitz.open(source_path)
        page = doc[0]  # Work on the first page

        # --- Define styles and positions ---
        top_margin = 20  # How far from the top to insert text (moved up)
        side_margin = 30  # How far from the sides
        font_size = 10
        text_color = (0, 0, 0)  # Black color

        # Position for Top Right Text (ROC)
        roc_text_len = fitz.get_text_length(
            roc_text, fontname="helv", fontsize=font_size
        )
        pos_right = fitz.Point(page.rect.width - roc_text_len - side_margin, top_margin)

        # Position for Top Center Text (Unique ID)
        id_text_len = fitz.get_text_length(
            unique_id, fontname="helv", fontsize=font_size
        )
        pos_center = fitz.Point(page.rect.width / 2 - id_text_len / 2, top_margin)

        # --- Insert the text (removed left-side custom text) ---
        page.insert_text(
            pos_center, unique_id, fontsize=font_size, fontname="helv", color=text_color
        )
        page.insert_text(
            pos_right, roc_text, fontsize=font_size, fontname="helv", color=text_color
        )

        # Save the modified document
        doc.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"Error adding labels to PDF: {e}")
        return False
