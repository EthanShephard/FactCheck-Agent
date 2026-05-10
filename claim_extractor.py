import fitz  # PyMuPDF
import re


def extract_text_from_pdf(pdf_file):
    """
    Extracts all text content from an uploaded PDF file.

    Args:
        pdf_file: Uploaded PDF file object from Streamlit.

    Returns:
        str: Combined text from all pages.
    """
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        return full_text

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def extract_claims(text):
    """
    Extracts lines containing factual claims such as:
    - Percentages
    - Monetary values
    - Years/dates
    - Large statistics

    Args:
        text (str): Full extracted text from PDF.

    Returns:
        list: Unique factual claims.
    """

    patterns = [
        r'.*\d+%.*',                                # Percentages (e.g. 45%)
        r'.*\$\d+.*',                               # Dollar values (e.g. $10M)
        r'.*\d{4}.*',                               # Years (e.g. 2024)
        r'.*\d+\s?(million|billion|trillion).*',   # Large numbers
        r'.*\d+\s?(users|customers|companies).*',  # User/company metrics
        r'.*\d+\s?(x|times).*',                     # Multipliers
    ]

    claims = []
    lines = text.split('\n')

    for line in lines:
        clean_line = line.strip()

        # Ignore very short lines
        if len(clean_line) < 15:
            continue

        for pattern in patterns:
            if re.search(pattern, clean_line, re.IGNORECASE):
                claims.append(clean_line)
                break

    # Remove duplicates while preserving structure
    unique_claims = list(set(claims))

    return unique_claims